import logging
from models.db_logs import DBLogs
from database import SessionLocal

# Configure logging (this should ideally be in your main config, but adding here for simplicity)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

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
        logging.info(f"User {user_id} performed '{action}' on {target_type} (ID: {target_id})")
    except Exception as e:
        session.rollback()
        logging.error(f"Failed to log action for User {user_id} - Action: {action}, Target: {target_type} (ID: {target_id}) | Error: {str(e)}")
    finally:
        session.close()
