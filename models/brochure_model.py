
from pydantic import BaseModel
from typing import Optional
from datetime import date

class BrochureBase(BaseModel):
    tags: Optional[List[str]] = []
    title: str
    description: Optional[str] = None
    code: Optional[str] = None
    slug: Optional[str] = None
    image_url: Optional[str] = None
    branch_id: Optional[int] = None
    start_date: Optional[date] = None
    expiry_date: Optional[date] = None
    infinite: bool = False

class BrochureCreate(BrochureBase):
    pass

class BrochureUpdate(BaseModel):
    title: Optional[str]
    description: Optional[str]
    code: Optional[str]
    slug: Optional[str]
    image_url: Optional[str]
    start_date: Optional[date]
    expiry_date: Optional[date]
    infinite: Optional[bool]

class Brochure(BrochureBase):
    id: int

    class Config:
        from_attributes = True
