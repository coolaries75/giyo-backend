from utils.logging_db_util import log_action

# Test parameters
user_id = 1
action = "CREATE"
target_type = "brochure"
target_id = 101
description = "Test log entry for brochure creation."

# Call the log function
log_action(user_id, action, target_type, target_id, description)
