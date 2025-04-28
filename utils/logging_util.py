# utils/logging_util.py

from datetime import datetime

def log_debug_action(message: str):
    _log("DEBUG", message)

def log_admin_action(admin_name: str, role: str, action: str):
    full_message = f"{admin_name} ({role}) performed action: {action}"
    _log("ADMIN", full_message)

def log_db_action(message: str):
    _log("DB", message)

def _log(log_type: str, message: str):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{log_type}] [{timestamp}] {message}")
