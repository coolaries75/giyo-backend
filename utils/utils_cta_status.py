# utils_cta_status.py

from urllib.parse import quote

def generate_cta_link_service(service):
    """Generate booking link for services"""
    return f"/book/{service.slug}" if getattr(service, "slug", None) else None

def calculate_service_status(service):
    """Determine service status"""
    if getattr(service, "is_active", False):
        return "active"
    return "inactive"

def generate_whatsapp_cta_link_ar(phone_number, title, item_code=None, item_type="item"):
    """
    Generate WhatsApp CTA link with proper Arabic/RTL support
    Args:
        phone_number: Recipient phone number (965XXXXXXXX)
        title: Main display text
        item_code: Optional item code (default None)
        item_type: Type of item (default "item")
    """
    if not phone_number:
        return None

    # Build message with fallbacks
    message_parts = []
    if title:
        message_parts.append(title)
    if item_code:
        message_parts.append(f"كود: {item_code}")
    message_parts.append("Giyo Clinic")
    
    message = " - ".join(message_parts)
    encoded_message = quote(message)
    
    return f"https://wa.me/{phone_number}?text={encoded_message}"