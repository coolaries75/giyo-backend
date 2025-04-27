def apply_pagination(query, page: int = 1, limit: int = 20):
    total = query.count()
    items = query.offset((page - 1) * limit).limit(limit).all()
    meta = {
        "page": page,
        "limit": limit,
        "total_items": total,
        "total_pages": (total + limit - 1) // limit
    }
    return items, meta
