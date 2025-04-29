# Trigger redeploy - no code change
# FastAPI main app with API versioning and CORS setup
from fastapi import FastAPI
from database import engine, Base
from routers import services, brochures, info
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Initialize Database
Base.metadata.create_all(bind=engine)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://giyo-frontend.vercel.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers with API Versioning
app.include_router(services.router, prefix="/api/v1/services", tags=["Services"])
app.include_router(brochures.router, prefix="/api/v1/brochures", tags=["Brochures"])
app.include_router(info.router, prefix="/api/v1", tags=["Info"])

@app.get("/")
def read_root():
    return {"message": "Welcome to Giyo Backend API. Use /api/v1/ for endpoints."}