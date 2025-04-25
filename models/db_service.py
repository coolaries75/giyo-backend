from sqlalchemy import Column, Integer, String, Numeric, Boolean
from database import Base

class ServiceDB(Base):
    __tablename__ = "services"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(String)
    price = Column(Numeric)
    code = Column(String, unique=True, index=True)
    slug = Column(String, unique=True, index=True)
    image_url = Column(String)
    branch_id = Column(Integer)
    is_active = Column(Boolean, default=True)
