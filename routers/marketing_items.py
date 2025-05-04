from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from database import get_db

router = APIRouter(tags=["Marketing Items"])

@router.get("/test")
def test_marketing_item():
    return {"message": "Marketing endpoint is reachable"}

# 🚧 Placeholder endpoints for future implementation
@router.post("/")
def create_marketing_item(
    item: dict,
    db: Session = Depends(get_db),
    x_admin_branch: int = Header(default=None)
):
    raise HTTPException(status_code=501, detail="Not implemented yet")

@router.get("/")
def get_marketing_items(
    db: Session = Depends(get_db),
    x_admin_branch: int = Header(default=None)
):
    raise HTTPException(status_code=501, detail="Not implemented yet")
