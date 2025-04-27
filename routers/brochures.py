from fastapi import APIRouter, HTTPException, Request
from typing import List
from database import SessionLocal
from models.brochure_model import Brochure
from response_wrapper import success_response, error_response
from role_check_util import check_role
from logging_db_util import log_db_action
from logging_debug_util import log_debug_action
from pagination_util import paginate

router = APIRouter()
db = SessionLocal()

class BrochureResponse:
    def __init__(self, id, title, code, status, cta_link):
        self.id = id
        self.title = title
        self.code = code
        self.status = status
        self.cta_link = cta_link

@router.get("/", response_model=List[BrochureResponse])
def get_brochures(request: Request, skip: int = 0, limit: int = 10):
    try:
        brochures = db.query(Brochure).filter(Brochure.is_deleted == False).offset(skip).limit(limit).all()
        result = []
        for b in brochures:
            status = "archived" if b.is_active == False else "active"
            if b.start_date:
                status = "upcoming"
            if b.expiry_date:
                status = "expired"
            result.append(BrochureResponse(
                id=b.id,
                title=b.title,
                code=b.code,
                status=status,
                cta_link=f"https://wa.me/965XXXXXXX?text=مرحباً، أود الاستفسار عن العرض {b.code}"
            ))
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/", response_model=dict)
def create_brochure(request: Request, brochure: Brochure):
    admin_token = request.headers.get("x_admin_token")
    admin_name = request.headers.get("x_admin_name")
    role = check_role(admin_token)

    try:
        db.add(brochure)
        db.commit()
        db.refresh(brochure)
        log_db_action(db, admin_name, role, f"Created brochure {brochure.id}")
        log_debug_action(f"{admin_name} ({role}) created brochure ID {brochure.id}")
        return success_response("Brochure created", {"id": brochure.id})
    except Exception as e:
        db.rollback()
        return error_response(str(e))

@router.put("/{brochure_id}")
def update_brochure(request: Request, brochure_id: int, brochure_data: dict):
    try:
        brochure = db.query(Brochure).filter(Brochure.id == brochure_id, Brochure.is_deleted == False).first()
        if not brochure:
            return error_response("Brochure not found")
        for key, value in brochure_data.items():
            setattr(brochure, key, value)
        db.commit()
        return success_response("Brochure updated")
    except Exception as e:
        db.rollback()
        return error_response(str(e))

@router.delete("/{brochure_id}")
def delete_brochure(request: Request, brochure_id: int):
    admin_token = request.headers.get("x_admin_token")
    admin_name = request.headers.get("x_admin_name")
    role = check_role(admin_token)

    try:
        brochure = db.query(Brochure).filter(Brochure.id == brochure_id).first()
        if not brochure:
            return error_response("Brochure not found")

        if role == "super_admin":
            db.delete(brochure)
            log_debug_action(f"{admin_name} (super_admin) permanently deleted brochure {brochure_id}")
        else:
            brochure.is_deleted = True
            log_debug_action(f"{admin_name} ({role}) soft deleted brochure {brochure_id}")

        db.commit()
        log_db_action(db, admin_name, role, f"Deleted brochure {brochure_id}")
        return success_response("Brochure deleted")
    except Exception as e:
        db.rollback()
        return error_response(str(e))
