from sqlalchemy import PickleType
from sqlalchemy.ext.mutable import MutableList

from sqlalchemy import Column, Integer, String, Boolean, Date
from database import Base

class BrochureDB(Base):
    tags = Column(MutableList.as_mutable(PickleType), default=list)
    __tablename__ = "brochures"

    id = Column(Integer, primary_key=True, index=True)
    branch_id = Column(Integer)
    title = Column(String)
    description = Column(String)
    code = Column(String, unique=True)
    slug = Column(String, unique=True)
    image_url = Column(String)
    start_date = Column(Date, nullable=True)
    expiry_date = Column(Date, nullable=True)
    infinite = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
