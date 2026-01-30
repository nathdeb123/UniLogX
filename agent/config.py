import os
from datetime import datetime

# Collection Settings
COLLECTION_INTERVAL = 5  # seconds
# Place logs under the user's Documents folder for packaged executables
BASE_LOG_DIR = os.path.join(os.path.expanduser("~"), "Documents", "UniLogX", "Log")
LOG_INDEX_FILE = os.path.join(BASE_LOG_DIR, "logs_index.jsonl")
SHUTDOWN_SIGNAL_FILE = os.path.join(BASE_LOG_DIR, "shutdown.signal")  # Signal file for graceful shutdown

# Log Storage Format (JSON Lines for ELK-like behavior)
LOG_FORMAT = "json"

# Categories
WINDOWS_CATEGORIES = ["system", "security", "application", "setup", "network"]
LINUX_CATEGORIES = ["syslog", "auth", "kernel", "audit", "cron", "services"]

# Retention Policy
MAX_LOGS_PER_FILE = 1000
LOG_ROTATION_SIZE = 50 * 1024 * 1024  # 50MB

# Dashboard Settings
DASHBOARD_PORT = 8501
DASHBOARD_HOST = "localhost"

# Log Levels
LOG_LEVELS = ["CRITICAL", "ERROR", "WARNING", "INFO", "DEBUG"]

# Enable Features
ENABLE_SEARCH = True
ENABLE_ANALYTICS = True
ENABLE_ALERTS = True

# Debug Mode
DEBUG = True


