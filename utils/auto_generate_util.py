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