from fastapi import APIRouter
from utils.response_wrapper import success_response

router = APIRouter()

@router.get("/schedule/info")
def get_schedule_info():
    return success_response(message="Schedule module coming soon.")
