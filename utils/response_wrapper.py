def success_response(data=None, meta=None):
    response = {"status": "success", "data": data}
    if meta:
        response["meta"] = meta
    return response

def error_response(message="An error occurred", code=400):
    return {"status": "error", "message": message, "code": code}
