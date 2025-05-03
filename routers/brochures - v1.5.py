# Brochures router with pagination and response wrapper
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Request, Header
from sqlalchemy.orm import Session
from database import SessionLocal
from models.db_brochure import BrochureDB
from models.brochure_model import Brochure, BrochureCreate, BrochureUpdate
from utils.logging_db_util import log_admin_action as log_db_action
from utils.logging_debug_util import log_admin_action as log_debug_action
from utils.role_check_util import check_role
from utils.response_wrapper import success_response, error_response
from utils.pagination_util import apply_pagination
from typing import List
from datetime import date
from urllib.parse import urlencode

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def generate_cta_link_brochure(brochure):
    if not brochure:
        return ""
    params = {
        "brochure_id": brochure.id,
        "brochure_title": brochure.title_ar
    }
    base_url = "https://yourclinic.com/brochures"  # Placeholder
    return f"{base_url}?{urlencode(params, encoding='utf-8')}"

def calculate_status(brochure):
    today = date.today()
    if not brochure.is_active:
        return "archived"
    elif brochure.infinite:
        return "active"
    elif brochure.start_date and brochure.start_date > today:
        return "scheduled"
    elif brochure.expiry_date and brochure.expiry_date < today:
        return "archived"
    else:
        return "active"

@router.get("/")
def get_brochures(page: int = 1, limit: int = 20, db: Session = Depends(get_db)):
    brochures = db.query(BrochureDB).all()
    result = []
    for b in brochures:
        b_data = Brochure.from_orm(b).dict()
        # Inject CTA link
        b_data["cta_link"] = generate_cta_link_brochure(b)
        # Inject Status
        b_data["status"] = calculate_status(b)
        result.append(b_data)
    paginated = apply_pagination(result, page, limit)
    return success_response(data=paginated, message="Brochures fetched successfully")

@router.post("/", response_model=Brochure)
def create_brochure(brochure: BrochureCreate, request: Request, x_admin_token: str = Header(...), db: Session = Depends(get_db)):
    role = check_role(x_admin_token)
    if role not in ["super_admin", "post_admin"]:
        raise HTTPException(status_code=403, detail="Insufficient permissions")

    payload = brochure.dict()
    if "tags" not in payload:
        payload["tags"] = []

    if "price" not in payload:
        payload["price"] = None
    if "slug" not in payload:
        payload["slug"] = None

    # Code logic
    if "code" not in payload or not payload["code"]:
        now = datetime.utcnow()
        prefix = now.strftime("%m%y") + "-BUN-"
        last = db.query(BrochureDB).filter(BrochureDB.code.like(f"{prefix}%")).order_by(BrochureDB.id.desc()).first()
        last_num = int(last.code[-3:]) if last and last.code else 0
        new_code = f"{prefix}{last_num + 1:03d}"
        while db.query(BrochureDB).filter(BrochureDB.code == new_code).first():
            last_num += 1
            new_code = f"{prefix}{last_num + 1:03d}"
        payload["code"] = new_code
    else:
        if db.query(BrochureDB).filter(BrochureDB.code == payload["code"]).first():
            raise HTTPException(status_code=409, detail=f"Brochure code '{payload['code']}' already exists.")

    
    role = check_role(x_admin_token)
    admin_branch_id = int(request.headers.get("x-admin-branch", "0"))
    if role in ["branch_admin", "post_admin"]:
        payload["branch_id"] = admin_branch_id
    elif role == "super_admin":
        if not payload.get("branch_id"):
            payload["branch_id"] = 1  # fallback default

    if not payload.get("tags"):
        payload["tags"] = [f"auto", f"branch-{payload['branch_id']}"]
    payload["tags"] = list(dict.fromkeys([t.lower() for t in payload["tags"]]))  # deduplicate and normalize

    db_brochure = BrochureDB(**payload)
    db.add(db_brochure)
    db.commit()
    db.refresh(db_brochure)

    admin_user = request.headers.get("x-admin-name", "unknown")
    log_db_action(db, admin_user, role, "Create", "Brochure", db_brochure.id)
    log_debug_action(admin_user, "Create", "Brochure", db_brochure.id)

    return success_response(data=Brochure.from_orm(db_brochure).dict(), message="Brochure created successfully")

@router.put("/{brochure_id}", response_model=Brochure)
def update_brochure(brochure_id: int, brochure: BrochureUpdate, request: Request, x_admin_token: str = Header(...), db: Session = Depends(get_db)):
    role = check_role(x_admin_token)
    if role not in ["super_admin", "post_admin"]:
        raise HTTPException(status_code=403, detail="Insufficient permissions")

    db_brochure = db.query(BrochureDB).filter(BrochureDB.id == brochure_id).first()
    if not db_brochure:
        return error_response(message="Brochure not found", code=404)
    updates = brochure.dict(exclude_unset=True)
    if "tags" not in updates:
        updates["tags"] = db_brochure.tags or []
    for key, value in updates.items():
        setattr(db_brochure, key, value)
    db.commit()
    db.refresh(db_brochure)

    admin_user = request.headers.get("x-admin-name", "unknown")
    log_db_action(db, admin_user, role, "Update", "Brochure", db_brochure.id)
    log_debug_action(admin_user, "Update", "Brochure", db_brochure.id)

    return success_response(data=Brochure.from_orm(db_brochure).dict(), message="Brochure updated successfully")

@router.delete("/{brochure_id}")
def delete_brochure(brochure_id: int, request: Request, x_admin_token: str = Header(...), db: Session = Depends(get_db)):
    role = check_role(x_admin_token)
    if role not in ["super_admin", "post_admin"]:
        raise HTTPException(status_code=403, detail="Insufficient permissions")

    db_brochure = db.query(BrochureDB).filter(BrochureDB.id == brochure_id).first()
    if not db_brochure:
        return error_response(message="Brochure not found", code=404)
    db_brochure.is_active = False
    db.commit()

    admin_user = request.headers.get("x-admin-name", "unknown")
    log_db_action(db, admin_user, role, "Archive", "Brochure", db_brochure.id)
    log_debug_action(admin_user, "Archive", "Brochure", db_brochure.id)

    return success_response(message="Brochure archived successfully")

@router.delete("/{brochure_id}/permanent")
def hard_delete_brochure(brochure_id: int, x_admin_token: str = Header(...), db: Session = Depends(get_db)):
    role = check_role(x_admin_token)
    if role != "super_admin":
        raise HTTPException(status_code=403, detail="Insufficient permissions")

    brochure = db.query(BrochureDB).filter(BrochureDB.id == brochure_id).first()
    if not brochure:
        return error_response(message="Brochure not found", code=404)

    db.delete(brochure)
    db.commit()

    return success_response(message="Brochure permanently deleted")


@router.post("/{brochure_id}/duplicate", response_model=Brochure)
def duplicate_brochure(brochure_id: int, overrides: BrochureUpdate, request: Request, x_admin_token: str = Header(...), db: Session = Depends(get_db)):
    role = check_role(x_admin_token)
    if role not in ["super_admin", "post_admin"]:
        raise HTTPException(status_code=403, detail="Insufficient permissions")

    original = db.query(BrochureDB).filter(BrochureDB.id == brochure_id, BrochureDB.is_active == True).first()
    if not original:
        return error_response(message="Original brochure not found", code=404)

    original_data = {
        "title_ar": original.title_ar,
        "description_ar": original.description_ar,
        "start_date": original.start_date,
        "expiry_date": original.expiry_date,
        "infinite": original.infinite,
        "branch_id": original.branch_id,
        "tags": original.tags or []
    }
    override_data = overrides.dict(exclude_unset=True)
    combined_data = {**original_data, **override_data}

    duplicated = BrochureDB(**combined_data)
    db.add(duplicated)
    db.commit()
    db.refresh(duplicated)

    admin_user = request.headers.get("x-admin-name", "unknown")
    log_db_action(db, admin_user, role, "Duplicate", "Brochure", duplicated.id)
    log_debug_action(admin_user, "Duplicate", "Brochure", duplicated.id)

    return success_response(data=Brochure.from_orm(duplicated).dict(), message="Brochure duplicated successfully")


# TODO: Migrate role-checking to JWT/OAuth in future versions.
# TODO: Implement multilingual responses in future versions.
