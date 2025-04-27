import logging
from models.db_logs import DBLogs
from database import SessionLocal

# Configure logging only if not already configured
if not logging.getLogger().hasHandlers():
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def log_action(user_id, action, target_type, target_id, description=None):
    """
    Logs an action performed by a user into the database and console.

    Parameters:
        user_id (int): ID of the user performing the action.
        action (str): Description of the action.
        target_type (str): The type of object affected (e.g., 'brochure', 'service').
        target_id (int): ID of the target object.
        description (str, optional): Additional details about the action.
    """
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
        logging.error(f"[DB LOG ERROR] User {user_id} - Action: {action} on {target_type} (ID: {target_id}) | Error: {str(e)}")
    finally:
        session.close()
