from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models.db_service import ServiceDB as Service
from models.db_brochure import Brochure
from utils.utils_cta_status import generate_whatsapp_cta_link_ar
from datetime import datetime
from pydantic import BaseModel
from datetime import date

router = APIRouter(tags=["Marketing Items"])

@router.get("/test")
def test_marketing_item():
    return {"message": "Marketing endpoint is reachable"}

@router.get("/")
def get_marketing_items(
    db: Session = Depends(get_db),
    x_admin_branch: int = Header(default=None)
):
    now = datetime.utcnow()

    services = db.query(Service).filter(
        Service.branch_id == x_admin_branch,
        Service.soft_delete == False
    ).all()

    brochures = db.query(Brochure).filter(
        Brochure.branch_id == x_admin_branch,
        Brochure.soft_delete == False
    ).all()

    service_items = [
        {
            "type": "service",
            "title": svc.title,
            "status": "active",  # placeholder since determine_status not defined
            "cta": generate_whatsapp_cta_link_ar(svc.title, svc.phone),
            "category": svc.category,
            "start_date": svc.start_date,
            "end_date": svc.expiry_date
        }
        for svc in services
    ]

    brochure_items = [
        {
            "type": "brochure",
            "title": bro.title,
            "status": "active",  # placeholder since determine_status not defined
            "cta": generate_whatsapp_cta_link_ar(bro.title, bro.phone),
            "category": bro.category,
            "start_date": bro.start_date,
            "end_date": bro.expiry_date
        }
        for bro in brochures
    ]

    return service_items + brochure_items

# ---------- POST ENDPOINT START ----------
class MarketingItemCreate(BaseModel):
    title: str
    description: str
    start_date: date
    end_date: date
    cta_type: str
    cta_value: str
    status: str

@router.post("/")
def create_marketing_item(payload: MarketingItemCreate):
    if payload.cta_type != "whatsapp":
        raise HTTPException(status_code=400, detail="Only WhatsApp CTA supported in this test.")

    cta_link = generate_whatsapp_cta_link_ar(payload.title, payload.cta_value)

    return {
        "title": payload.title,
        "description": payload.description,
        "start_date": payload.start_date,
        "end_date": payload.end_date,
        "status": payload.status,
        "cta_link": cta_link
    }
# ---------- POST ENDPOINT END ----------
