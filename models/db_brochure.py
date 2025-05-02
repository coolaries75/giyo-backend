from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy import Column, Integer, String, Boolean, Date, Numeric
from database import Base

class BrochureDB(Base):
    __tablename__ = "brochures"

    id = Column(Integer, primary_key=True, index=True)
    branch_id = Column(Integer)
    title = Column(String)
    description = Column(String)
    code = Column(String, unique=True)
    slug = Column(String, unique=True)
    image_url = Column(String)
    start_date = Column(Date, nullable=True)
    price = Column(Numeric, nullable=True)  # 🔁 moved higher
    expiry_date = Column(Date, nullable=True)
    infinite = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    tags = Column(ARRAY(String), nullable=True, default=[])
