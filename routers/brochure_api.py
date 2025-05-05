import os
from uuid import uuid4, UUID
from fastapi import APIRouter, Depends, HTTPException, Header, Form, File, UploadFile
from sqlalchemy.orm import Session
from models.db_brochure import Brochure
from database import get_db
from utils.utils_cta_status import generate_whatsapp_cta_link_ar
from datetime import date, datetime
from copy import deepcopy
from typing import Optional, List


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
    try:
        start_date_parsed = datetime.strptime(start_date, "%Y-%m-%d").date() if start_date else None
        end_date_parsed = datetime.strptime(end_date, "%Y-%m-%d").date() if end_date else None

        # ✅ Save image with unique filename
        ext = os.path.splitext(image.filename)[-1]
        unique_filename = f"{uuid4().hex}{ext}"
        # Ensure the target directory exists at runtime (for Railway or fresh deploys)
        os.makedirs("static/brochures", exist_ok=True)
        save_path = f"static/brochures/{unique_filename}"
        with open(save_path, "wb") as buffer:
            buffer.write(await image.read())

        brochure_data = {
            "title": title,
            "description": description,
            "category": category,
            "price": price,
            "slug": slug,
            "start_date": start_date_parsed,
            "expiry_date": end_date_parsed,
            "cta_override": cta_override,
            "code": code,
            "status": status,
            "cta_phone": cta_phone,
            "image_url": f"/static/brochures/{unique_filename}"
        }

        new_brochure = Brochure(**brochure_data)

        if x_admin_branch is not None:
            new_brochure.branch_id = x_admin_branch

        today = date.today()
        if start_date_parsed and start_date_parsed > today:
            new_brochure.status = "coming_soon"
        elif end_date_parsed and end_date_parsed < today:
            new_brochure.status = "expired"
        else:
            new_brochure.status = status

        db.add(new_brochure)
        db.commit()
        db.refresh(new_brochure)

        new_brochure.cta_link = generate_whatsapp_cta_link_ar(
            phone_number=cta_phone,
            items=[{"name": new_brochure.title, "code": new_brochure.code}],
            item_type="brochure"
        )

        db.commit()
        db.refresh(new_brochure)
        return {"success": True, "id": new_brochure.id, "cta_link": new_brochure.cta_link}

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error creating brochure: {str(e)}")

# ---------- GET Brochures ----------
@router.get("/", response_model=List[dict])
def get_brochures(
    branch_id: Optional[int] = None,
    db: Session = Depends(get_db),
    x_admin_branch: Optional[int] = Header(default=None)
):
    query = db.query(Brochure).filter(Brochure.is_deleted == False)
    if branch_id:
        query = query.filter(Brochure.branch_id == branch_id)
    elif x_admin_branch:
        query = query.filter(Brochure.branch_id == x_admin_branch)
    results = query.order_by(Brochure.created_at.desc()).all()
    return [b.to_dict() for b in results]

# ---------- GET One Brochure ----------
@router.get("/{brochure_id}", response_model=dict)
def get_brochure(brochure_id: UUID, db: Session = Depends(get_db)):
    brochure = db.query(Brochure).filter(Brochure.id == brochure_id, Brochure.is_deleted == False).first()
    if not brochure:
        raise HTTPException(status_code=404, detail="Brochure not found")
    return brochure.to_dict()

# ---------- PUT Update ----------
@router.put("/{brochure_id}")
def update_brochure(
    brochure_id: UUID,
    brochure_update: dict,
    db: Session = Depends(get_db)
):
    brochure = db.query(Brochure).filter(Brochure.id == brochure_id, Brochure.is_deleted == False).first()
    if not brochure:
        raise HTTPException(status_code=404, detail="Brochure not found")

    for key, value in brochure_update.items():
        setattr(brochure, key, value)

    if "title" in brochure_update or "cta_phone" in brochure_update:
        if getattr(brochure, "title", None) and getattr(brochure, "cta_phone", None):
            brochure.cta_link = generate_whatsapp_cta_link_ar(
                phone_number=brochure.cta_phone,
                items=[{"name": brochure.title, "code": brochure.code}],
                item_type="brochure"
            )

    today = date.today()
    if getattr(brochure, "start_date", None) and brochure.start_date > today:
        brochure.status = "coming_soon"
    elif getattr(brochure, "expiry_date", None) and brochure.expiry_date < today:
        brochure.status = "expired"
    else:
        brochure.status = brochure_update.get("status", brochure.status)

    db.commit()
    db.refresh(brochure)
    return {"success": True, "id": brochure.id, "cta_link": brochure.cta_link}

# ---------- DELETE / RESTORE / ARCHIVE ----------
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

# ---------- DUPLICATE ----------
@router.post("/{brochure_id}/duplicate")
def duplicate_brochure(brochure_id: UUID, db: Session = Depends(get_db)):
    original = db.query(Brochure).filter(Brochure.id == brochure_id, Brochure.is_deleted == False).first()
    if not original:
        raise HTTPException(status_code=404, detail="Original brochure not found")

    duplicated = deepcopy(original)
    duplicated.id = uuid4()
    duplicated.code = None
    duplicated.status = "active"
    duplicated.created_at = None
    duplicated.updated_at = None

    db.add(duplicated)
    db.commit()
    db.refresh(duplicated)

    return {"success": True, "id": duplicated.id, "message": "Brochure duplicated"}

#   T o u c h   t o   t r i g g e r   R a i l w a y   r e d e p l o y
