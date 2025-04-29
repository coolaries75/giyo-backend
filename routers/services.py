# Services router with pagination and response wrapper
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

@router.get("/")
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

    db_service = ServiceDB(**service.dict())
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
    for key, value in service.dict(exclude_unset=True).items():
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

# TODO: Migrate role-checking to JWT/OAuth in future versions.
# TODO: Implement multilingual responses in future versions.
