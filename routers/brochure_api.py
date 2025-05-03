# brochure_api.py
if __name__ == "__main__":
    exit("Disabled crash route from running on deploy")
from fastapi import APIRouter, HTTPException, Request, Depends
from sqlalchemy.orm import Session
from database import get_db
from models.db_brochure import BrochureDB
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import date

router = APIRouter(tags=["brochures"])

# ✅ Response model to fix FastAPI 500 validation error
class BrochureResponse(BaseModel):
    success: bool
    id: int

# Pydantic input model
class BrochureCreate(BaseModel):
    title: str
    description: Optional[str] = None
    code: str
    slug: str
    image_url: Optional[str] = None
    start_date: Optional[date] = None
    expiry_date: Optional[date] = None
    infinite: Optional[bool] = False
    is_active: Optional[bool] = True
    tags: List[str] = Field(default_factory=list)
    price: Optional[float] = None
    status: Optional[str] = "active"

# ✅ Use response_model to enforce return structure
@router.post("/", response_model=BrochureResponse)
def create_brochure(req: Request, brochure: BrochureCreate, db: Session = Depends(get_db)):
    branch_id = req.headers.get("x-admin-branch")
    if not branch_id:
        raise HTTPException(status_code=400, detail="Missing branch ID header")

    new_brochure = BrochureDB(
        branch_id=int(branch_id),
        title=brochure.title,
        description=brochure.description,
        code=brochure.code,
        slug=brochure.slug,
        image_url=brochure.image_url,
        start_date=brochure.start_date,
        expiry_date=brochure.expiry_date,
        infinite=brochure.infinite,
        is_active=brochure.is_active,
        tags=brochure.tags,
        price=brochure.price,
        status=brochure.status
    )

    db.add(new_brochure)
    db.commit()
    db.refresh(new_brochure)
    return {"success": True, "id": new_brochure.id}
