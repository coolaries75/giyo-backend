from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from database import SessionLocal
from models.db_brochure import BrochureDB
from models.brochure_model import Brochure, BrochureCreate
from utils.auto_generate_util import generate_unique_slug, generate_unique_code
from utils.logging_db_util import log_admin_action as log_db_action
from utils.logging_debug_util import log_admin_action as log_debug_action
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

@router.post("/", response_model=Brochure)
def create_brochure(brochure: BrochureCreate, request: Request, db: Session = Depends(get_db)):
    base_slug = brochure.slug or brochure.title.lower().replace(" ", "-")
    unique_slug = generate_unique_slug(base_slug, db, BrochureDB)

    prefix = "BR-2024"
    unique_code = generate_unique_code(prefix, db, BrochureDB)

    db_brochure = BrochureDB(
        **brochure.dict(exclude={"slug", "code"}),
        slug=unique_slug,
        code=unique_code
    )
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