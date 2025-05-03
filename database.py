import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import Session
# from database import SessionLocal
from dotenv import load_dotenv
load_dotenv()



def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Database URL from environment variables
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable is not set.")

# SQLAlchemy setup
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Import models to ensure they are registered before table creation
from models import db_service, db_brochure

# Initialize Database
def init_db():
    print("🔧 Starting table creation...")
    Base.metadata.create_all(bind=engine)
    print("✅ Table creation completed for all registered models.")
