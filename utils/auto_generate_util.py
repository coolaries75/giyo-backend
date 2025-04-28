def generate_unique_slug(base_slug, db, model):
    slug = base_slug
    suffix = 1
    while db.query(model).filter(model.slug == slug).first():
        slug = f"{base_slug}-{suffix}"
        suffix += 1
    return slug

def generate_unique_code(prefix, db, model):
    suffix = 1
    code = f"{prefix}-{suffix:03d}"
    while db.query(model).filter(model.code == code).first():
        suffix += 1
        code = f"{prefix}-{suffix:03d}"
    return code
def generate_whatsapp_cta(code: str, country_code: str = "965") -> str:
    """
    Generates a WhatsApp CTA link with the given brochure or service code.
    """
    base_url = f"https://wa.me/{country_code}XXXXXXXX"
    message = f"مرحباً، أود الاستفسار عن العرض {code}"
    return f"{base_url}?text={message}"
