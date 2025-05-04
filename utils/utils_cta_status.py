# utils_cta_status.py

from urllib.parse import quote

def generate_cta_link_service(service):
    return f"/book/{service.slug}" if getattr(service, "slug", None) else None

def calculate_service_status(service):
    if getattr(service, "is_active", False):
        return "active"
    return "inactive"

def generate_whatsapp_cta_link_ar(phone_number, title, item_type="item"):
    """
    Generate a WhatsApp CTA link with Unicode-safe, emoji-safe, and Arabic/RTL-safe formatting.
    Includes a fallback if title is missing.
    """
    if not phone_number:
        return None

    if title:
        message = f"{title} - Giyo Clinic"
    else:
        message = f"{phone_number} - Giyo Clinic"

    encoded_message = quote(message)
    return f"https://wa.me/{phone_number}?text={encoded_message}"
