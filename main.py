# Touch trigger for redeploy - 2025-05-05 23:59
# FastAPI main app with API versioning and CORS setup

import logging
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from database import engine, Base
from routers import services, brochure_api_v2 as brochure_api, info
from routers import marketing_items
from auth_api import router as auth_router

# Configure logging FIRST
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()  # Log to console
    ]
)

logger = logging.getLogger(__name__)
logger.info("Initializing FastAPI application")

app = FastAPI()

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")
logger.info("Static files mounted at /static")

@app.get("/health")
def health_check():
    logger.debug("Health check endpoint accessed")
    return {"status": "ok"}

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://giyo-frontend.vercel.app",  # ✅ Production frontend
        "http://localhost:5173"              # ✅ Dev frontend (Vite)
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
logger.info("CORS middleware configured")

# Include Routers with API Versioning
app.include_router(auth_router)
app.include_router(services.router, prefix="/api/v1/services", tags=["Services"])
app.include_router(brochure_api.router, prefix="/api/v1/brochures", tags=["Brochures"])
app.include_router(info.router, prefix="/api/v1", tags=["Info"])
app.include_router(marketing_items.router, prefix="/api/v1/marketing-items", tags=["Marketing Items"])
logger.info("All routers mounted")

@app.get("/")
def read_root():
    logger.debug("Root endpoint accessed")
    return {"message": "Welcome to Giyo Backend API. Use /api/v1/ for endpoints."}

logger.info("Application startup complete")