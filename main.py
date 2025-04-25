from fastapi import FastAPI
from routers import services, brochures
from database import init_db  # Import the init_db function

app = FastAPI()

# Initialize Database (Auto-create tables if they don't exist)
init_db()

# Include routers
app.include_router(services.router, prefix="/api/services", tags=["Services"])
app.include_router(brochures.router, prefix="/api/brochures", tags=["Brochures"])

# Root endpoint
@app.get("/")
def read_root():
    return {"message": "Giyo Clinic Backend is Running"}

# Note: No uvicorn.run here - Railway handles ASGI app startup
