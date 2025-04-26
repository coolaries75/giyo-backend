# Info endpoint implementation
from fastapi import APIRouter
from utils.response_wrapper import success_response

router = APIRouter()

@router.get("/info")
def get_api_info():
    routes = [
        "/api/v1/brochures",
        "/api/v1/services",
        "/api/v1/info"
    ]
    return success_response(
        data={"routes": routes},
        message="Giyo API v1.4 is operational."
    )