from models.db_logs import DBLogs
from database import SessionLocal

def log_action(user_id, action, target_type, target_id, description=None):
    session = SessionLocal()
    try:
        log_entry = DBLogs(
            user_id=user_id,
            action=action,
            target_type=target_type,
            target_id=target_id,
            description=description
        )
        session.add(log_entry)
        session.commit()
        print(f"[LOG SUCCESS] User {user_id} performed {action} on {target_type} (ID: {target_id})")
    except Exception as e:
        session.rollback()
        print(f"[LOG ERROR] Failed to log action for User {user_id}: {e}")
    finally:
        session.close()
