from datetime import datetime

# General-purpose debug logger matching your imports
def log_debug_action(message):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {message}")

# Preserve existing detailed admin logger for future structured logs
def log_admin_action(admin_user, action, target_type, target_id):
    admin_name = admin_user if admin_user else "System"
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{timestamp}] Admin '{admin_name}' performed '{action}' on {target_type} ID {target_id}"
    print(log_entry)

