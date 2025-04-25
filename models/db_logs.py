
from sqlalchemy import Column, Integer, String, Text, TIMESTAMP
from database import Base

class AdminActionLog(Base):
    __tablename__ = "admin_action_logs"

    id = Column(Integer, primary_key=True, index=True)
    admin_name = Column(String(100))
    role = Column(String(50))
    action = Column(String(50))
    item_type = Column(String(50))
    item_id = Column(Integer)
    notes = Column(Text)
    timestamp = Column(TIMESTAMP)
