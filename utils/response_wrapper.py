# Standardized response formatting utility
def success_response(data=None, message="Operation successful"):
    return {
        "status": "success",
        "data": data,
        "message": message
    }

def error_response(message="An error occurred", code=400):
    return {
        "status": "error",
        "message": message,
        "code": code
    }