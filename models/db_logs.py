from sqlalchemy import Column, Integer, String, Text, TIMESTAMP
from database import Base
from datetime import datetime

class DBLogs(Base):
    __tablename__ = "admin_action_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer)
    action = Column(String(50))
    target_type = Column(String(50))
    target_id = Column(Integer)
    description = Column(Text)
    timestamp = Column(TIMESTAMP, default=datetime.utcnow)
