from datetime import datetime
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy import Column, Integer, String, Numeric, Boolean, DateTime
from database import Base

class ServiceDB(Base):
    __tablename__ = "services"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(String)
    price = Column(Numeric)
    code = Column(String, unique=True, index=True)
    slug = Column(String, unique=True, index=True)
    branch_id = Column(Integer) # moved higher to trigger redeploy
    image_url = Column(String)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    tags = Column(ARRAY(String), nullable=True, default=[])
