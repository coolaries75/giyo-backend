# setup_db.py

from database import engine, Base

def initialize_database():
    print("Creating all tables...")
    Base.metadata.create_all(bind=engine)
    print("✅ Tables created successfully.")

if __name__ == "__main__":
    initialize_database()
