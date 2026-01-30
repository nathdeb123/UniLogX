import os
import json
from datetime import datetime
import socket

LOG_FILES = {
    "/var/log/syslog": "syslog",
    "/var/log/auth.log": "auth",
    "/var/log/kern.log": "kernel",
    "/var/log/audit/audit.log": "audit",
    "/var/log/cron": "cron"
}

def parse_log_line(line, category):
    """Parse a single log line into JSON format"""
    try:
        # Basic parsing for common Linux log formats
        # Format: Month Day Time Hostname Process[PID]: Message
        parts = line.strip().split(maxsplit=4)
        
        if len(parts) >= 3:
            timestamp = f"{datetime.now().year} {' '.join(parts[:3])}"
            try:
                parsed_time = datetime.strptime(timestamp, "%Y %b %d %H:%M:%S")
            except:
                parsed_time = datetime.now()
            
            message = parts[4] if len(parts) > 4 else line.strip()
            
            log_entry = {
                "timestamp": parsed_time.isoformat(),
                "message": message,
                "category": category,
                "os_type": "linux",
                "host": socket.gethostname(),
                "level": "INFO"
            }
            
            # Detect log level
            if any(x in message.upper() for x in ["ERROR", "CRITICAL", "FAILED"]):
                log_entry["level"] = "ERROR"
            elif any(x in message.upper() for x in ["WARNING", "WARN"]):
                log_entry["level"] = "WARNING"
            elif "DEBUG" in message.upper():
                log_entry["level"] = "DEBUG"
            
            return log_entry
    except Exception as e:
        pass
    
    return None

def collect_linux_logs(base_path):
    """Collect Linux system logs and store as JSON"""
    hostname = socket.gethostname()
    
    for src, folder in LOG_FILES.items():
        if os.path.exists(src):
            try:
                logs = []
                # Read last 500 lines from each log file
                with open(src, 'r', encoding='utf-8', errors='ignore') as f:
                    lines = f.readlines()[-500:]
                
                for line in lines:
                    log_entry = parse_log_line(line, folder)
                    if log_entry:
                        logs.append(log_entry)
                
                # Save logs to JSON file
                if logs:
                    log_file = os.path.join(
                        base_path, 
                        folder, 
                        f"{folder}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                    )
                    
                    with open(log_file, 'w', encoding='utf-8') as f:
                        for log in logs:
                            f.write(json.dumps(log) + '\n')
                    
                    print(f"[+] Collected {len(logs)} logs from {folder}")
            except PermissionError:
                print(f"[!] Permission denied accessing {src}")
            except Exception as e:
                print(f"[!] Error collecting {folder}: {str(e)}")

