from fastapi import APIRouter, Request
from typing import List
from sqlalchemy.orm import Session
from database import SessionLocal
from models.brochure_model import Brochure
from utils.response_wrapper import success_response, error_response
from utils.role_check_util import check_role
from utils.logging_util import log_debug_action
from utils.pagination_util import apply_pagination
from routers.schemas.brochure_schema import BrochureResponse
from utils.auto_generate_util import generate_whatsapp_cta

router = APIRouter(prefix="/api/v1/brochures", tags=["Brochures"])

@router.get("/", response_model=List[BrochureResponse])
def get_brochures(request: Request, page: int = 1, limit: int = 10):
    session: Session = SessionLocal()
    try:
        query = session.query(Brochure).filter(Brochure.is_deleted == False)
        brochures, meta = apply_pagination(query, page, limit)
        result = []
        for b in brochures:
            status = "archived" if not b.is_active else "active"
            if b.start_date:
                status = "upcoming"
            if b.expiry_date:
                status = "expired"
            result.append(BrochureResponse(
                id=b.id,
                title=b.title,
                code=b.code,
                status=status,
                cta_link=generate_whatsapp_cta(b.code)
            ))
        return success_response(result, meta)
    except Exception as e:
        return error_response(str(e))
    finally:
        session.close()

@router.post("/", response_model=dict)
def create_brochure(request: Request, brochure: Brochure):
    session: Session = SessionLocal()
    admin_token = request.headers.get("x_admin_token")
    admin_name = request.headers.get("x_admin_name")
    role = check_role(admin_token)

    try:
        session.add(brochure)
        session.commit()
        session.refresh(brochure)
        log_debug_action(f"{admin_name} ({role}) created brochure ID {brochure.id}")
        return success_response({"message": "Brochure created", "id": brochure.id})
    except Exception as e:
        session.rollback()
        return error_response(str(e))
    finally:
        session.close()

@router.put("/{brochure_id}")
def update_brochure(request: Request, brochure_id: int, brochure_data: dict):
    session: Session = SessionLocal()
    try:
        brochure = session.query(Brochure).filter(Brochure.id == brochure_id, Brochure.is_deleted == False).first()
        if not brochure:
            return error_response("Brochure not found")
        for key, value in brochure_data.items():
            setattr(brochure, key, value)
        session.commit()
        return success_response({"message": "Brochure updated"})
    except Exception as e:
        session.rollback()
        return error_response(str(e))
    finally:
        session.close()

@router.delete("/{brochure_id}")
def delete_brochure(request: Request, brochure_id: int):
    session: Session = SessionLocal()
    admin_token = request.headers.get("x_admin_token")
    admin_name = request.headers.get("x_admin_name")
    role = check_role(admin_token)

    try:
        brochure = session.query(Brochure).filter(Brochure.id == brochure_id).first()
        if not brochure:
            return error_response("Brochure not found")

        if role == "super_admin":
            session.delete(brochure)
            log_debug_action(f"{admin_name} (super_admin) permanently deleted brochure {brochure_id}")
        else:
            brochure.is_deleted = True
            log_debug_action(f"{admin_name} ({role}) soft deleted brochure {brochure_id}")

        session.commit()
        return success_response({"message": "Brochure deleted"})
    except Exception as e:
        session.rollback()
        return error_response(str(e))
    finally:
        session.close()

