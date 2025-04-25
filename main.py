from fastapi import FastAPI
from routers import services, brochures

app = FastAPI()

# Include routers
app.include_router(services.router, prefix="/api/services", tags=["Services"])
app.include_router(brochures.router, prefix="/api/brochures", tags=["Brochures"])

# Root endpoint
@app.get("/")
def read_root():
    return {"message": "Giyo Clinic Backend is Running"}

# Note: No uvicorn.run here - Railway will handle ASGI app startup