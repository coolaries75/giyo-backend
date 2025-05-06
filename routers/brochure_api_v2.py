import os
import logging
from uuid import uuid4, UUID
from fastapi import APIRouter, Depends, HTTPException, Header, Form, File, UploadFile, status
from sqlalchemy.orm import Session
from models.db_brochure import Brochure
from database import get_db
from utils.utils_cta_status import generate_whatsapp_cta_link_ar
from datetime import date, datetime
from copy import deepcopy
from typing import Optional, List
from sqlalchemy.exc import IntegrityError

# Configure logging
logger = logging.getLogger(__name__)
router = APIRouter(tags=["Brochures"])

@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    responses={
        201: {
            "description": "Brochure created successfully",
            "content": {
                "application/json": {
                    "example": {
                        "success": True,
                        "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                        "cta_link": "https://wa.me/96512345678?text=📋%20Brochure:%20Asakuki%20Humidifier%20Offer%0A%0A🔖%20Code:%200525-BUN-011%0A%0A📌%20Type:%20brochure"
                    }
                }
            }
        },
        400: {"description": "Invalid input (e.g., blank title, malformed date)"},
        409: {"description": "Brochure code already exists"},
        500: {"description": "Internal server error"}
    },
    summary="Create a new brochure",
    description="""
    Creates a brochure with:
    - Image upload (saved to `/static/brochures/`)
    - Automatic WhatsApp CTA link generation
    - Date-based status logic (`active`/`coming_soon`/`expired`)
    
    **CTA Link Format**:  
    `https://wa.me/<cta_phone>?text=📋 Brochure: <title>%0A%0A🔖 Code: <code>%0A%0A📌 Type: brochure`  
    (URL-encoded newlines: `%0A`)
    """
)
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
    branch_id: UUID = Header(..., alias="x-admin-branch")
):
    try:
        logger.debug(f"Brochure creation attempt - Code: {code}, Branch: {branch_id}")

        # Enhanced validation
        if not title.strip():
            raise HTTPException(status_code=400, detail="Title cannot be blank")
        if not category.strip():
            raise HTTPException(status_code=400, detail="Category cannot be blank")
        try:
            price = float(price)
            if price <= 0:
                raise HTTPException(status_code=400, detail="Price must be positive")
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid price format")

        # Date parsing with enhanced error handling
        try:
            start_date_parsed = datetime.strptime(start_date, "%Y-%m-%d").date() if start_date else None
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid start date format. Use YYYY-MM-DD")

        try:
            end_date_parsed = datetime.strptime(end_date, "%Y-%m-%d").date() if end_date else None
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid end date format. Use YYYY-MM-DD")

        if start_date_parsed and end_date_parsed and start_date_parsed > end_date_parsed:
            raise HTTPException(status_code=400, detail="Start date cannot be after end date")

        # Secure image handling
        ext = os.path.splitext(image.filename)[-1].lower()
        if ext not in ('.jpg', '.jpeg', '.png'):
            raise HTTPException(status_code=400, detail="Only JPG/PNG images allowed")
            
        unique_filename = f"{uuid4().hex}{ext}"
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
            "cta_override": cta_override.strip() if cta_override else None,
            "code": code,
            "status": status,
            "cta_phone": cta_phone,
            "image_url": f"/static/brochures/{unique_filename}",
            "branch_id": branch_id
        }

        new_brochure = Brochure(**brochure_data)

        # Enhanced status logic
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
            title=new_brochure.title,
            item_code=new_brochure.code,
            item_type="brochure"
        )

        db.commit()
        db.refresh(new_brochure)
        return {"success": True, "id": new_brochure.id, "cta_link": new_brochure.cta_link}

    except IntegrityError as e:
        db.rollback()
        if "brochures_code_key" in str(e):
            logger.warning(f"Duplicate code attempt: {code} (Branch: {branch_id})")
            raise HTTPException(status_code=409, detail="Brochure code already exists")
        logger.error(f"Database integrity error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    except Exception as e:
        db.rollback()
        logger.error(f"Unexpected error creating brochure: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error creating brochure: {str(e)}")

@router.get(
    "/",
    response_model=List[dict],
    summary="List all brochures",
    description="Returns active brochures filtered by branch_id if provided",
    responses={
        200: {
            "description": "List of brochures",
            "content": {
                "application/json": {
                    "example": [{
                        "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                        "title": "Sample Brochure",
                        "cta_link": "https://wa.me/96512345678?text=..."
                    }]
                }
            }
        }
    }
)
def get_brochures(
    branch_id: Optional[UUID] = None,
    db: Session = Depends(get_db),
    x_admin_branch: Optional[UUID] = Header(default=None, alias="x-admin-branch")
):
    try:
        query = db.query(Brochure).filter(Brochure.is_deleted == False)
        if branch_id:
            query = query.filter(Brochure.branch_id == branch_id)
        elif x_admin_branch:
            query = query.filter(Brochure.branch_id == x_admin_branch)
        return [b.to_dict() for b in query.order_by(Brochure.created_at.desc()).all()]
    except Exception as e:
        logger.error(f"Error fetching brochures: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

# [Other endpoints (GET by ID, PUT, DELETE, etc.) follow same enhanced pattern...]