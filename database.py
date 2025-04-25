import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable is not set.")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Auto-create tables
def init_db():
    try:
        from models import db_service, db_brochure
        print("✅ Imported models successfully.")
        
        print("🚀 Starting table creation...")
        Base.metadata.create_all(bind=engine)
        print("✅ Table creation completed.")
        
    except Exception as e:
        print(f"❌ Error during init_db: {e}")
        import sys
        sys.exit(1)   # Force app to exit with error
