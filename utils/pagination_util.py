# Pagination logic utility
def apply_pagination(data_list, page=1, limit=20):
    start = (page - 1) * limit
    end = start + limit
    paginated_data = data_list[start:end]
    return {
        "page": page,
        "limit": limit,
        "total_items": len(data_list),
        "items": paginated_data
    }