import os
from agent.config import BASE_LOG_DIR

def create_folders(os_type):
    os_folder = "win" if os_type == "windows" else "LinX"
    base = os.path.join(BASE_LOG_DIR, os_folder)

    categories = {
        "windows": ["system", "security", "application", "setup", "network"],
        "linux": ["syslog", "auth", "kernel", "audit", "cron", "services"]
    }

    for cat in categories[os_type]:
        os.makedirs(os.path.join(base, cat), exist_ok=True)

    return base
