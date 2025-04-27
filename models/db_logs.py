from sqlalchemy import Column, Integer, String, DateTime, func
from database import Base

class LogEntry(Base):
    __tablename__ = "logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False)
    action = Column(String(50), nullable=False)
    target_type = Column(String(50), nullable=False)  # e.g., 'brochure', 'service'
    target_id = Column(Integer, nullable=False)
    details = Column(String(255), nullable=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
