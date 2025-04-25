from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from database import SessionLocal
from models.db_brochure import BrochureDB
from models.brochure_model import Brochure, BrochureCreate, BrochureUpdate
from utils.logging_db_util import log_admin_action as log_db_action
from utils.logging_debug_util import log_admin_action as log_debug_action
from typing import List
from datetime import date

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def calculate_status(brochure: BrochureDB):
    today = date.today()
    if not brochure.is_active:
        return "archived"
    if brochure.infinite:
        return "active"
    if brochure.start_date and brochure.start_date > today:
        return "scheduled"
    if brochure.expiry_date and brochure.expiry_date < today:
        return "archived"
    return "active"

@router.get("/", response_model=List[Brochure])
def get_brochures(db: Session = Depends(get_db)):
    brochures = db.query(BrochureDB).all()
    result = []
    for b in brochures:
        b_data = Brochure.from_orm(b).dict()
        b_data["status"] = calculate_status(b)
        result.append(b_data)
    return result

@router.post("/", response_model=Brochure)
def create_brochure(brochure: BrochureCreate, request: Request, db: Session = Depends(get_db)):
    db_brochure = BrochureDB(**brochure.dict())
    db.add(db_brochure)
    db.commit()
    db.refresh(db_brochure)

    admin_user = request.headers.get("x-admin-name", "unknown")
    role = request.headers.get("x-api-role", "unknown")
    log_db_action(db, admin_user, role, "Create", "Brochure", db_brochure.id)
    log_debug_action(admin_user, "Create", "Brochure", db_brochure.id)

    b_data = Brochure.from_orm(db_brochure).dict()
    b_data["status"] = calculate_status(db_brochure)
    return b_data

@router.put("/{brochure_id}", response_model=Brochure)
def update_brochure(brochure_id: int, brochure: BrochureUpdate, request: Request, db: Session = Depends(get_db)):
    db_brochure = db.query(BrochureDB).filter(BrochureDB.id == brochure_id).first()
    if not db_brochure:
        raise HTTPException(status_code=404, detail="Brochure not found")
    for key, value in brochure.dict(exclude_unset=True).items():
        setattr(db_brochure, key, value)
    db.commit()
    db.refresh(db_brochure)

    admin_user = request.headers.get("x-admin-name", "unknown")
    role = request.headers.get("x-api-role", "unknown")
    log_db_action(db, admin_user, role, "Update", "Brochure", db_brochure.id)
    log_debug_action(admin_user, "Update", "Brochure", db_brochure.id)

    b_data = Brochure.from_orm(db_brochure).dict()
    b_data["status"] = calculate_status(db_brochure)
    return b_data

@router.delete("/{brochure_id}")
def delete_brochure(brochure_id: int, request: Request, db: Session = Depends(get_db)):
    db_brochure = db.query(BrochureDB).filter(BrochureDB.id == brochure_id, BrochureDB.is_active == True).first()
    if not db_brochure:
        raise HTTPException(status_code=404, detail="Brochure not found or already archived")
    db_brochure.is_active = False
    db.commit()

    admin_user = request.headers.get("x-admin-name", "unknown")
    role = request.headers.get("x-api-role", "unknown")
    log_db_action(db, admin_user, role, "Archive", "Brochure", db_brochure.id)
    log_debug_action(admin_user, "Archive", "Brochure", db_brochure.id)

    return {"detail": "Brochure archived successfully"}

@router.delete("/{brochure_id}/permanent")
def hard_delete_brochure(brochure_id: int, request: Request, db: Session = Depends(get_db)):
    db_brochure = db.query(BrochureDB).filter(BrochureDB.id == brochure_id).first()
    if not db_brochure:
        raise HTTPException(status_code=404, detail="Brochure not found")
    db.delete(db_brochure)
    db.commit()

    admin_user = request.headers.get("x-admin-name", "unknown")
    role = request.headers.get("x-api-role", "unknown")
    log_db_action(db, admin_user, role, "Hard Delete", "Brochure", brochure_id)
    log_debug_action(admin_user, "Hard Delete", "Brochure", brochure_id)

    return {"detail": "Brochure permanently deleted"}