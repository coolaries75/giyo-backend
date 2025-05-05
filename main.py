# Touch trigger for redeploy - 2025-05-05 23:59
# FastAPI main app with API versioning and CORS setup

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from database import engine, Base
from routers import services, brochure_api, info
from routers import marketing_items

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/health")
def health_check():
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

# Include Routers with API Versioning
app.include_router(services.router, prefix="/api/v1/services", tags=["Services"])
app.include_router(brochure_api.router, prefix="/api/v1/brochures", tags=["Brochures"])
app.include_router(info.router, prefix="/api/v1", tags=["Info"])
app.include_router(marketing_items.router, prefix="/api/v1/marketing-items", tags=["Marketing Items"])

@app.get("/")
def read_root():
    return {"message": "Welcome to Giyo Backend API. Use /api/v1/ for endpoints."}
