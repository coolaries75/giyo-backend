# Brochures router with pagination and response wrapper
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

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

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

@router.get("/", response_model=List[Brochure])
def get_brochures(page: int = 1, limit: int = 20, db: Session = Depends(get_db)):
    brochures = db.query(BrochureDB).all()
    result = []
    for b in brochures:
        b_data = Brochure.from_orm(b).dict()
        b_data["status"] = calculate_status(b)
        result.append(b_data)
    paginated = apply_pagination(result, page, limit)
    return success_response(data=paginated, message="Brochures fetched successfully")

@router.post("/", response_model=Brochure)
def create_brochure(brochure: BrochureCreate, request: Request, x_admin_token: str = Header(...), db: Session = Depends(get_db)):
    role = check_role(x_admin_token)
    if role not in ["super_admin", "post_admin"]:
        raise HTTPException(status_code=403, detail="Insufficient permissions")

    db_brochure = BrochureDB(**brochure.dict())
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
    for key, value in brochure.dict(exclude_unset=True).items():
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

# TODO: Migrate role-checking to JWT/OAuth in future versions.
# TODO: Implement multilingual responses in future versions.