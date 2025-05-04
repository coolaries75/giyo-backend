from utils.utils_cta_status import generate_cta_link_service, calculate_service_status
# Services router with pagination and response wrapper
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Request, Header
from sqlalchemy.orm import Session
from database import SessionLocal
from models.db_service import ServiceDB
from models.service_model import Service, ServiceCreate, ServiceUpdate
from utils.logging_db_util import log_admin_action as log_db_action
from utils.logging_debug_util import log_admin_action as log_debug_action
from utils.role_check_util import check_role
from utils.response_wrapper import success_response, error_response
from utils.pagination_util import apply_pagination
from typing import List
from urllib.parse import urlencode
from typing import Optional

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def generate_cta_link_service(service):
    if not service:
        return ""
    params = {
        "service_id": service.id,
        "service_title": service.title_ar
    }
    base_url = "https://yourclinic.com/booking"  # Placeholder
    return f"{base_url}?{urlencode(params, encoding='utf-8')}"

def calculate_service_status(service):
    return "active" if service.is_active else "archived"

def get_services(page: int = 1, limit: int = 20, db: Session = Depends(get_db)):
    services = db.query(ServiceDB).filter(ServiceDB.is_active == True).all()
    result = []
    for s in services:
        s_data = Service.from_orm(s).dict()
        # Inject CTA link
        s_data["cta_link"] = generate_cta_link_service(s)
        # Inject Status
        s_data["status"] = calculate_service_status(s)
        result.append(s_data)
    paginated = apply_pagination(result, page, limit)
    return success_response(data=paginated, message="Services fetched successfully")

@router.post("/", response_model=Service)
def create_service(service: ServiceCreate, request: Request, x_admin_token: str = Header(...), db: Session = Depends(get_db)):
    role = check_role(x_admin_token)
    if role not in ["super_admin", "post_admin"]:
        raise HTTPException(status_code=403, detail="Insufficient permissions")

    payload = service.dict()
    if "branch_id" not in payload:
        payload["branch_id"] = None
    if "slug" not in payload:
        payload["slug"] = None
    if "tags" not in payload:
        payload["tags"] = []

    # Auto-generate code if not supplied
    if "code" not in payload or not payload["code"]:
        now = datetime.utcnow()
        prefix = now.strftime("%m%y") + "-SER-"
        last = db.query(ServiceDB).filter(ServiceDB.code.like(f"{prefix}%")).order_by(ServiceDB.id.desc()).first()
        last_num = int(last.code[-3:]) if last and last.code else 0
        new_code = f"{prefix}{last_num + 1:03d}"
        while db.query(ServiceDB).filter(ServiceDB.code == new_code).first():
            last_num += 1
            new_code = f"{prefix}{last_num + 1:03d}"
        payload["code"] = new_code
    else:
        if db.query(ServiceDB).filter(ServiceDB.code == payload["code"]).first():
            raise HTTPException(status_code=409, detail=f"Service code '{payload['code']}' already exists.")

    
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

    db_service = ServiceDB(**payload)
    db.add(db_service)
    db.commit()
    db.refresh(db_service)

    admin_user = request.headers.get("x-admin-name", "unknown")
    log_db_action(db, admin_user, role, "Create", "Service", db_service.id)
    log_debug_action(admin_user, "Create", "Service", db_service.id)

    return success_response(data=Service.from_orm(db_service).dict(), message="Service created successfully")

@router.put("/{service_id}", response_model=Service)
def update_service(service_id: int, service: ServiceUpdate, request: Request, x_admin_token: str = Header(...), db: Session = Depends(get_db)):
    role = check_role(x_admin_token)
    if role not in ["super_admin", "post_admin"]:
        raise HTTPException(status_code=403, detail="Insufficient permissions")

    db_service = db.query(ServiceDB).filter(ServiceDB.id == service_id, ServiceDB.is_active == True).first()
    if not db_service:
        return error_response(message="Service not found", code=404)
    updates = service.dict(exclude_unset=True)
    if "branch_id" not in updates:
        updates["branch_id"] = db_service.branch_id
    if "code" not in updates:
        updates["code"] = db_service.code
    if "slug" not in updates:
        updates["slug"] = db_service.slug
    if "tags" not in updates:
        updates["tags"] = db_service.tags or []
    for key, value in updates.items():
        setattr(db_service, key, value)
    db.commit()
    db.refresh(db_service)

    admin_user = request.headers.get("x-admin-name", "unknown")
    log_db_action(db, admin_user, role, "Update", "Service", db_service.id)
    log_debug_action(admin_user, "Update", "Service", db_service.id)

    return success_response(data=Service.from_orm(db_service).dict(), message="Service updated successfully")

@router.delete("/{service_id}")
def delete_service(service_id: int, request: Request, x_admin_token: str = Header(...), db: Session = Depends(get_db)):
    role = check_role(x_admin_token)
    if role not in ["super_admin", "post_admin"]:
        raise HTTPException(status_code=403, detail="Insufficient permissions")

    db_service = db.query(ServiceDB).filter(ServiceDB.id == service_id, ServiceDB.is_active == True).first()
    if not db_service:
        return error_response(message="Service not found", code=404)
    db_service.is_active = False
    db.commit()

    admin_user = request.headers.get("x-admin-name", "unknown")
    log_db_action(db, admin_user, role, "Archive", "Service", db_service.id)
    log_debug_action(admin_user, "Archive", "Service", db_service.id)

    return success_response(message="Service archived successfully")

@router.delete("/{service_id}/permanent")
def hard_delete_service(service_id: int, x_admin_token: str = Header(...), db: Session = Depends(get_db)):
    role = check_role(x_admin_token)
    if role != "super_admin":
        raise HTTPException(status_code=403, detail="Insufficient permissions")

    service = db.query(ServiceDB).filter(ServiceDB.id == service_id).first()
    if not service:
        return error_response(message="Service not found", code=404)

    db.delete(service)
    db.commit()

    return success_response(message="Service permanently deleted")


@router.post("/{service_id}/duplicate", response_model=Service)
def duplicate_service(service_id: int, overrides: ServiceUpdate, request: Request, x_admin_token: str = Header(...), db: Session = Depends(get_db)):
    role = check_role(x_admin_token)
    if role not in ["super_admin", "post_admin"]:
        raise HTTPException(status_code=403, detail="Insufficient permissions")

    original = db.query(ServiceDB).filter(ServiceDB.id == service_id, ServiceDB.is_active == True).first()
    if not original:
        return error_response(message="Original service not found", code=404)

    # Create payload based on original, with override fields applied
    original_data = {
        "name": original.name,
        "description": original.description,
        "price": original.price,
        "tags": original.tags or []
    }
    override_data = overrides.dict(exclude_unset=True)
    combined_data = {**original_data, **override_data}

    duplicated = ServiceDB(**combined_data)
    db.add(duplicated)
    db.commit()
    db.refresh(duplicated)

    admin_user = request.headers.get("x-admin-name", "unknown")
    log_db_action(db, admin_user, role, "Duplicate", "Service", duplicated.id)
    log_debug_action(admin_user, "Duplicate", "Service", duplicated.id)

    return success_response(data=Service.from_orm(duplicated).dict(), message="Service duplicated successfully")


# TODO: Migrate role-checking to JWT/OAuth in future versions.
# TODO: Implement multilingual responses in future versions.

@router.get("/", response_model=List[Service])
def get_services(
    page: int = 1,
    limit: int = 20,
    branch_id: Optional[int] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(ServiceDB)
    if branch_id:
        query = query.filter(ServiceDB.branch_id == branch_id)
    services = query.all()
    result = []
    for s in services:
        s_data = Service.from_orm(s).dict()
        s_data["cta_link"] = generate_cta_link_service(s)
        s_data["status"] = calculate_service_status(s)
        if status and s_data["status"] != status:
            continue
        result.append(s_data)
    paginated = apply_pagination(result, page, limit)
    return success_response(data=paginated, message="Services fetched successfully")