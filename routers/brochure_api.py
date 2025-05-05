from fastapi import APIRouter, Depends, HTTPException, Header, Form, File, UploadFile
from sqlalchemy.orm import Session
from models.db_brochure import Brochure
from database import get_db
from utils.utils_cta_status import generate_whatsapp_cta_link_ar
from datetime import date

router = APIRouter(tags=["Brochures"])

@router.post("/")
async def create_brochure(
    title: str = Form(...),
    description: str = Form(...),
    category: str = Form(...),
    price: float = Form(...),
    slug: str = Form(None),
    start_date: str = Form(None),
    end_date: str = Form(None),
    cta_override: str = Form(None),
    code: str = Form(...),
    status: str = Form("active"),
    cta_phone: str = Form(...),
    image: UploadFile = File(...),
    db: Session = Depends(get_db),
    x_admin_branch: int = Header(default=None)
):
    brochure_data = {
        "title": title,
        "description": description,
        "category": category,
        "price": price,
        "slug": slug,
        "start_date": start_date,
        "expiry_date": end_date,
        "cta_override": cta_override,
        "code": code,
        "status": status,
        "cta_phone": cta_phone,
        "image_url": image.filename
    }

    new_brochure = Brochure(**brochure_data)

    if x_admin_branch is not None:
        new_brochure.branch_id = x_admin_branch

    new_brochure.cta_link = generate_whatsapp_cta_link_ar(
        phone_number=cta_phone,
        items=[{"name": name, "code": code}],
        item_type="brochure"
    )

    today = date.today()
    if start_date and start_date > str(today):
        new_brochure.status = "coming_soon"
    elif end_date and end_date < str(today):
        new_brochure.status = "expired"
    else:
        new_brochure.status = status

    db.add(new_brochure)
    db.commit()
    db.refresh(new_brochure)
    return {"success": True, "id": new_brochure.id, "cta_link": new_brochure.cta_link}

    new_brochure = Brochure(**brochure)

    # ✅ Inject branch_id if sent via header
    if x_admin_branch is not None:
        new_brochure.branch_id = x_admin_branch

    # ✅ CTA logic
    new_brochure.cta_link = generate_whatsapp_cta_link_ar(
        phone_number=brochure["cta_phone"],
        items=[{"name": brochure["name"], "code": brochure["code"]}],
        item_type="brochure"
    )

    # ✅ Status logic based on dates
    today = date.today()
    if brochure.get("start_date") and brochure["start_date"] > today:
        new_brochure.status = "coming_soon"
    elif brochure.get("end_date") and brochure["end_date"] < today:
        new_brochure.status = "expired"
    else:
        new_brochure.status = brochure.get("status", "active")

    db.add(new_brochure)
    db.commit()
    db.refresh(new_brochure)
    return {"success": True, "id": new_brochure.id, "cta_link": new_brochure.cta_link}

# --- Injected GET endpoints ---

from typing import Optional, List
from uuid import UUID

@router.get("/", response_model=List[dict])
def get_brochures(
    branch_id: Optional[int] = None,
    db: Session = Depends(get_db),
    x_admin_branch: Optional[int] = Header(default=None)
):
    query = db.query(Brochure).filter(Brochure.is_deleted == False)

    # Respect super admin override or fallback to branch header
    if branch_id:
        query = query.filter(Brochure.branch_id == branch_id)
    elif x_admin_branch:
        query = query.filter(Brochure.branch_id == x_admin_branch)

    results = query.order_by(Brochure.created_at.desc()).all()
    return [b.to_dict() for b in results]

@router.get("/{brochure_id}", response_model=dict)
def get_brochure(brochure_id: UUID, db: Session = Depends(get_db)):
    brochure = db.query(Brochure).filter(Brochure.id == brochure_id, Brochure.is_deleted == False).first()
    if not brochure:
        raise HTTPException(status_code=404, detail="Brochure not found")
    return brochure.to_dict()

# --- Injected PUT endpoint ---

@router.put("/{brochure_id}")
def update_brochure(
    brochure_id: UUID,
    brochure_update: dict,
    db: Session = Depends(get_db)
):
    brochure = db.query(Brochure).filter(Brochure.id == brochure_id, Brochure.is_deleted == False).first()
    if not brochure:
        raise HTTPException(status_code=404, detail="Brochure not found")

    # Update fields from input
    for key, value in brochure_update.items():
        setattr(brochure, key, value)

    # CTA logic re-evaluation
    if "name" in brochure_update or "cta_phone" in brochure_update:
        if getattr(brochure, "name", None) and getattr(brochure, "cta_phone", None):
            brochure.cta_link = generate_whatsapp_cta_link_ar(
                phone_number=brochure.cta_phone,
                items=[{"name": brochure.name, "code": brochure.code}],
                item_type="brochure"
            )

    # Status recalculation
    today = date.today()
    if getattr(brochure, "start_date", None) and brochure.start_date > today:
        brochure.status = "coming_soon"
    elif getattr(brochure, "end_date", None) and brochure.end_date < today:
        brochure.status = "expired"
    else:
        brochure.status = brochure_update.get("status", brochure.status)

    db.commit()
    db.refresh(brochure)
    return {"success": True, "id": brochure.id, "cta_link": brochure.cta_link}

# --- Injected DELETE / RESTORE / ARCHIVE / DUPLICATE endpoints ---

@router.delete("/{brochure_id}")
def delete_brochure(brochure_id: UUID, db: Session = Depends(get_db)):
    brochure = db.query(Brochure).filter(Brochure.id == brochure_id, Brochure.is_deleted == False).first()
    if not brochure:
        raise HTTPException(status_code=404, detail="Brochure not found")
    brochure.is_deleted = True
    db.commit()
    return {"success": True, "message": "Brochure soft deleted."}

@router.put("/{brochure_id}/restore")
def restore_brochure(brochure_id: UUID, db: Session = Depends(get_db)):
    brochure = db.query(Brochure).filter(Brochure.id == brochure_id, Brochure.is_deleted == True).first()
    if not brochure:
        raise HTTPException(status_code=404, detail="Brochure not found or not deleted")
    brochure.is_deleted = False
    db.commit()
    return {"success": True, "message": "Brochure restored."}

@router.put("/{brochure_id}/archive")
def archive_brochure(brochure_id: UUID, db: Session = Depends(get_db)):
    brochure = db.query(Brochure).filter(Brochure.id == brochure_id, Brochure.is_deleted == False).first()
    if not brochure:
        raise HTTPException(status_code=404, detail="Brochure not found")
    brochure.status = "archived"
    db.commit()
    return {"success": True, "message": "Brochure archived."}

@router.post("/{brochure_id}/duplicate")
def duplicate_brochure(brochure_id: UUID, db: Session = Depends(get_db)):
    original = db.query(Brochure).filter(Brochure.id == brochure_id, Brochure.is_deleted == False).first()
    if not original:
        raise HTTPException(status_code=404, detail="Original brochure not found")

    from uuid import uuid4
    from copy import deepcopy

    duplicated = deepcopy(original)
    duplicated.id = uuid4()
    duplicated.code = None  # let frontend or logic assign new code
    duplicated.status = "active"
    duplicated.created_at = None
    duplicated.updated_at = None
    db.add(duplicated)
    db.commit()
    db.refresh(duplicated)

    return {"success": True, "id": duplicated.id, "message": "Brochure duplicated"}

