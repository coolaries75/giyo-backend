from fastapi import APIRouter, HTTPException, Request
from typing import List
from database import SessionLocal
from utils.service_model import Service
from utils.response_wrapper import success_response, error_response
from utils.role_check_util import check_role
from utils.logging_db_util import log_db_action
from utils.logging_debug_util import log_debug_action
from util.pagination_util import paginate

router = APIRouter()
db = SessionLocal()

class ServiceResponse:
    def __init__(self, id, name, code, status, cta_link):
        self.id = id
        self.name = name
        self.code = code
        self.status = status
        self.cta_link = cta_link

@router.get("/", response_model=List[ServiceResponse])
def get_services(request: Request, skip: int = 0, limit: int = 10):
    try:
        services = db.query(Service).filter(Service.is_deleted == False).offset(skip).limit(limit).all()
        result = []
        for s in services:
            status = "archived" if not s.is_active else "active"
            result.append(ServiceResponse(
                id=s.id,
                name=s.name,
                code=s.code,
                status=status,
                cta_link=f"https://wa.me/965XXXXXXX?text=مرحباً، أود الاستفسار عن الخدمة {s.code}"
            ))
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/", response_model=dict)
def create_service(request: Request, service: Service):
    admin_token = request.headers.get("x_admin_token")
    admin_name = request.headers.get("x_admin_name")
    role = check_role(admin_token)

    try:
        db.add(service)
        db.commit()
        db.refresh(service)
        log_db_action(db, admin_name, role, f"Created service {service.id}")
        log_debug_action(f"{admin_name} ({role}) created service ID {service.id}")
        return success_response("Service created", {"id": service.id})
    except Exception as e:
        db.rollback()
        return error_response(str(e))

@router.put("/{service_id}")
def update_service(request: Request, service_id: int, service_data: dict):
    try:
        service = db.query(Service).filter(Service.id == service_id, Service.is_deleted == False).first()
        if not service:
            return error_response("Service not found")
        for key, value in service_data.items():
            setattr(service, key, value)
        db.commit()
        return success_response("Service updated")
    except Exception as e:
        db.rollback()
        return error_response(str(e))

@router.delete("/{service_id}")
def delete_service(request: Request, service_id: int):
    admin_token = request.headers.get("x_admin_token")
    admin_name = request.headers.get("x_admin_name")
    role = check_role(admin_token)

    try:
        service = db.query(Service).filter(Service.id == service_id).first()
        if not service:
            return error_response("Service not found")

        if role == "super_admin":
            db.delete(service)
            log_debug_action(f"{admin_name} (super_admin) permanently deleted service {service_id}")
        else:
            service.is_deleted = True
            log_debug_action(f"{admin_name} ({role}) soft deleted service {service_id}")

        db.commit()
        log_db_action(db, admin_name, role, f"Deleted service {service_id}")
        return success_response("Service deleted")
    except Exception as e:
        db.rollback()
        return error_response(str(e))

@router.delete("/permanent/{service_id}")
def hard_delete_service(request: Request, service_id: int):
    admin_token = request.headers.get("x_admin_token")
    role = check_role(admin_token)

    if role != "super_admin":
        return error_response("Unauthorized for permanent delete")

    try:
        service = db.query(Service).filter(Service.id == service_id).first()
        if not service:
            return error_response("Service not found")
        db.delete(service)
        db.commit()
        return success_response("Service permanently deleted")
    except Exception as e:
        db.rollback()
        return error_response(str(e))
