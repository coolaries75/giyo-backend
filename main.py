from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routers import brochures, services, info, schedule, docs_info

from database import Base, engine

app = FastAPI()

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://giyo-frontend.vercel.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database Initialization
Base.metadata.create_all(bind=engine)

# Routers
app.include_router(services.router, prefix="/api/v1/services")
app.include_router(brochures.router, prefix="/api/v1/brochures")
app.include_router(info.router, prefix="/api/v1/info")
app.include_router(schedule.router, prefix="/api/v1/schedule")
app.include_router(docs_info.router, prefix="/api/v1/docs-info")
