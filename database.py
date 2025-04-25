import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Load DATABASE_URL from environment variables
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable is not set.")

# SQLAlchemy setup
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Initialize Database (Auto-create tables)
def init_db():
    try:
        from models import db_service, db_brochure
        print("✅ Successfully loaded db_service and db_brochure models")
        Base.metadata.create_all(bind=engine)
        print("✅ Table creation completed.")
    except Exception as e:
        print(f"❌ Error during DB initialization: {e}")
