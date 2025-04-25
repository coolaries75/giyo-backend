from datetime import datetime

def log_admin_action(admin_user, action, target_type, target_id):
    admin_name = admin_user if admin_user else "System"
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{timestamp}] Admin '{admin_name}' performed '{action}' on {target_type} ID {target_id}"
    print(log_entry)