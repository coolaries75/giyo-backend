
from pydantic import BaseModel
from typing import Optional

class ServiceBase(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    code: str
    slug: Optional[str] = None
    image_url: Optional[str] = None
    branch_id: int

class ServiceCreate(ServiceBase):
    pass

class ServiceUpdate(BaseModel):
    name: Optional[str]
    description: Optional[str]
    price: Optional[float]
    code: Optional[str]
    slug: Optional[str]
    image_url: Optional[str]

class Service(ServiceBase):
    id: int

    class Config:
        from_attributes = True
