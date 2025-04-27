from fastapi import APIRouter
from utils.response_wrapper import success_response

router = APIRouter()

@router.get("/docs-info")
def get_docs_info():
    routes = [
        "/api/v1/brochures",
        "/api/v1/services",
        "/api/v1/schedule/info",
        "/api/v1/docs-info"
    ]
    return success_response(data={"available_routes": routes}, message="Giyo API documentation info.")
