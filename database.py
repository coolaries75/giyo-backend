import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Database URL from environment variables
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable is not set.")

# SQLAlchemy setup
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Import SQLAlchemy Models (register for Alembic/Future Migrations)
from models import Brochure, Service

# Initialize Database
def init_db():
    print("🔧 Starting table creation...")
    Base.metadata.create_all(bind=engine)
    print("✅ Table creation completed for all registered models.")

# Dependency for FastAPI endpoints (optional but professional)
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
