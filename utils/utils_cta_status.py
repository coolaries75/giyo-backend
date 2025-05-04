# utils_cta_status.py

def generate_cta_link_service(service):
    return f"/book/{service.slug}" if getattr(service, "slug", None) else None

def calculate_service_status(service):
    if getattr(service, "is_active", False):
        return "active"
    return "inactive"

# --- Injected Brochure CTA Generator ---

def generate_whatsapp_cta_link_ar(phone_number, items, item_type="item"):
    if not phone_number or not items:
        return None
    if isinstance(items, dict):
        items = [items]
    intro = f"📍 {item_type.capitalize()} للتواصل"
    lines = [f"{intro}:"]
    for i in items:
        label = i.get("name") or i.get("title") or "بدون اسم"
        code = i.get("code") or "-"
        lines.append(f"- {label} ({code})")
    lines.append("📲 أرسل لنا لحجز الموعد")
    message = "\n".join(lines)
    base_url = f"https://wa.me/{phone_number}"
    return f"{base_url}?text=" + message.replace(" ", "%20").replace("\n", "%0A")
