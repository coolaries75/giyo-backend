from datetime import datetime

def success_response(data=None, meta=None):
    return {
        "status": "success",
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "data": data,
        "meta": meta or {}
    }

def error_response(message="An error occurred", code=400):
    return {
        "status": "error",
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "message": message,
        "code": code
    }
