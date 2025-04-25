from sqlalchemy.orm import Session
from models.db_logs import AdminActionLog

def log_admin_action(db: Session, admin_name: str, role: str, action: str, item_type: str, item_id: int, notes: str = None):
    log_entry = AdminActionLog(
        admin_name=admin_name,
        role=role,
        action=action,
        item_type=item_type,
        item_id=item_id,
        notes=notes
    )
    db.add(log_entry)
    db.commit()