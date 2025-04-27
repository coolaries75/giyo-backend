from fastapi import APIRouter, HTTPException, Header
from sqlalchemy.orm import Session
from database import SessionLocal
from models.brochure_model import Brochure
from utils.logging_debug_util import log_debug_action
from utils.role_check_util import check_role

router = APIRouter(prefix="/api/v1/brochures", tags=["Brochures"])

# --- GET All Active Brochures ---
@router.get("/")
def get_brochures():
    session: Session = SessionLocal()
    try:
        brochures = session.query(Brochure).filter(Brochure.is_archived == False).all()
        return brochures
    finally:
        session.close()

# --- POST Create Brochure ---
@router.post("/")
def create_brochure(brochure: Brochure, x_admin_token: str = Header(...)):
    role, admin_name = check_role(x_admin_token)
    session: Session = SessionLocal()
    try:
        session.add(brochure)
        session.commit()
        log_debug_action(f"{admin_name} ({role}) created brochure ID {brochure.id}")
        return brochure
    finally:
        session.close()

# --- PUT Update Brochure ---
@router.put("/{brochure_id}")
def update_brochure(brochure_id: int, updated_data: Brochure, x_admin_token: str = Header(...)):
    role, admin_name = check_role(x_admin_token)
    session: Session = SessionLocal()
    try:
        brochure = session.query(Brochure).filter(Brochure.id == brochure_id).first()
        if not brochure:
            raise HTTPException(status_code=404, detail="Brochure not found")
        if brochure.is_archived:
            raise HTTPException(status_code=400, detail="Cannot update archived brochure")
        for field, value in updated_data.dict(exclude_unset=True).items():
            setattr(brochure, field, value)
        session.commit()
        log_debug_action(f"{admin_name} ({role}) updated brochure ID {brochure.id}")
        return brochure
    finally:
        session.close()

# --- DELETE Hard Delete (Super Admin Only) ---
@router.delete("/{brochure_id}")
def delete_brochure(brochure_id: int, x_admin_token: str = Header(...)):
    role, admin_name = check_role(x_admin_token)
    if role != "super_admin":
        raise HTTPException(status_code=403, detail="Only super admin can hard delete")
    session: Session = SessionLocal()
    try:
        brochure = session.query(Brochure).filter(Brochure.id == brochure_id).first()
        if not brochure:
            raise HTTPException(status_code=404, detail="Brochure not found")
        session.delete(brochure)
        session.commit()
        log_debug_action(f"{admin_name} ({role}) hard deleted brochure ID {brochure.id}")
        return {"detail": f"Brochure ID {brochure_id} permanently deleted"}
    finally:
        session.close()

# --- ARCHIVE Brochure ---
@router.put("/{brochure_id}/archive")
def archive_brochure(brochure_id: int, x_admin_token: str = Header(...)):
    role, admin_name = check_role(x_admin_token)
    session: Session = SessionLocal()
    try:
        brochure = session.query(Brochure).filter(Brochure.id == brochure_id).first()
        if not brochure:
            raise HTTPException(status_code=404, detail="Brochure not found")
        brochure.is_archived = True
        session.commit()
        log_debug_action(f"{admin_name} ({role}) archived brochure ID {brochure.id}")
        return {"detail": f"Brochure ID {brochure_id} archived"}
    finally:
        session.close()

# --- UNARCHIVE Brochure ---
@router.put("/{brochure_id}/unarchive")
def unarchive_brochure(brochure_id: int, x_admin_token: str = Header(...)):
    role, admin_name = check_role(x_admin_token)
    session: Session = SessionLocal()
    try:
        brochure = session.query(Brochure).filter(Brochure.id == brochure_id).first()
        if not brochure:
            raise HTTPException(status_code=404, detail="Brochure not found")
        brochure.is_archived = False
        session.commit()
        log_debug_action(f"{admin_name} ({role}) unarchived brochure ID {brochure.id}")
        return {"detail": f"Brochure ID {brochure_id} unarchived"}
    finally:
        session.close()
