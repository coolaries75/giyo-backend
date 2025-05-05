from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy import Column, Integer, String, Boolean, Date, Numeric, Text
from database import Base

class Brochure(Base):
    __tablename__ = "brochures"

    id = Column(Integer, primary_key=True, index=True)
    branch_id = Column(Integer)
    title = Column(String)
    description = Column(Text)
    category = Column(String, nullable=True)
    code = Column(String, unique=True)
    slug = Column(String, unique=True)
    image_url = Column(String)
    start_date = Column(Date, nullable=True)
    price = Column(Numeric, nullable=True)  # 🔁 moved higher
    expiry_date = Column(Date, nullable=True)
    infinite = Column(Boolean, default=False)
    tags = Column(ARRAY(Text), default=[])
cta_phone = Column(String)
cta_override = Column(String, nullable=True)
cta_link = Column(String)
status = Column(String, default="active")


