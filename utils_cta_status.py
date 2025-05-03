# utils_cta_status.py

def generate_cta_link_service(service):
    return f"/book/{service.slug}" if getattr(service, "slug", None) else None

def calculate_service_status(service):
    if getattr(service, "is_active", False):
        return "active"
    return "inactive"
