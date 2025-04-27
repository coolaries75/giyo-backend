import logging
from models.db_logs import LogEntry
from database import SessionLocal

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# --- Simple Debugging Utilities ---
def log_info(message: str):
    print(f"[INFO] {message}")

def log_error(message: str):
    print(f"[ERROR] {message}")

def log_debug(message: str):
    print(f"[DEBUG] {message}")

# --- Database Logging Function ---
def log_action(user_id: int, action: str, target_type: str, target_id: int, details: str = None):
    session = SessionLocal()
    try:
        log_entry = LogEntry(
            user_id=user_id,
            action=action,
            target_type=target_type,
            target_id=target_id,
            details=details
        )
        session.add(log_entry)
        session.commit()
        logging.info(f"Logged action: {action} by User {user_id} on {target_type} {target_id}")
    except Exception as e:
        session.rollback()
        logging.error(f"Failed to log action: {e}")
    finally:
        session.close()
