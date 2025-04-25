from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from database import SessionLocal
from models.db_service import ServiceDB
from models.service_model import Service, ServiceCreate, ServiceUpdate
from utils.logging_db_util import log_admin_action as log_db_action
from utils.logging_debug_util import log_admin_action as log_debug_action
from typing import List

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/", response_model=List[Service])
def get_services(db: Session = Depends(get_db)):
    services = db.query(ServiceDB).filter(ServiceDB.is_active == True).all()
    return services

@router.post("/", response_model=Service)
def create_service(service: ServiceCreate, request: Request, db: Session = Depends(get_db)):
    db_service = ServiceDB(**service.dict())
    db.add(db_service)
    db.commit()
    db.refresh(db_service)

    admin_user = request.headers.get("x-admin-name", "unknown")
    role = request.headers.get("x-api-role", "unknown")
    log_db_action(db, admin_user, role, "Create", "Service", db_service.id)
    log_debug_action(admin_user, "Create", "Service", db_service.id)

    return db_service

@router.put("/{service_id}", response_model=Service)
def update_service(service_id: int, service: ServiceUpdate, request: Request, db: Session = Depends(get_db)):
    db_service = db.query(ServiceDB).filter(ServiceDB.id == service_id, ServiceDB.is_active == True).first()
    if not db_service:
        raise HTTPException(status_code=404, detail="Service not found")
    for key, value in service.dict(exclude_unset=True).items():
        setattr(db_service, key, value)
    db.commit()
    db.refresh(db_service)

    admin_user = request.headers.get("x-admin-name", "unknown")
    role = request.headers.get("x-api-role", "unknown")
    log_db_action(db, admin_user, role, "Update", "Service", db_service.id)
    log_debug_action(admin_user, "Update", "Service", db_service.id)

    return db_service

@router.delete("/{service_id}")
def delete_service(service_id: int, request: Request, db: Session = Depends(get_db)):
    db_service = db.query(ServiceDB).filter(ServiceDB.id == service_id, ServiceDB.is_active == True).first()
    if not db_service:
        raise HTTPException(status_code=404, detail="Service not found")
    db_service.is_active = False
    db.commit()

    admin_user = request.headers.get("x-admin-name", "unknown")
    role = request.headers.get("x-api-role", "unknown")
    log_db_action(db, admin_user, role, "Archive", "Service", db_service.id)
    log_debug_action(admin_user, "Archive", "Service", db_service.id)

    return {"detail": "Service archived successfully"}