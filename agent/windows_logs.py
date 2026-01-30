import os
import json
import subprocess
import shutil
from datetime import datetime
import traceback

EVENT_PATH = r"C:\Windows\System32\winevt\Logs"

LOG_MAP = {
    "System.evtx": "system",
    "Security.evtx": "security",
    "Application.evtx": "application",
    "Setup.evtx": "setup"
}

def parse_windows_logs(log_file_path, category):
    """Parse Windows event log and return structured JSON logs"""
    logs = []
    try:
        # Use PowerShell to read Windows Event Logs
        ps_command = f"""
        Get-EventLog -LogName {category.capitalize()} -Newest 100 | 
        Select-Object TimeGenerated, Source, EventID, Message, Type |
        ConvertTo-Json
        """
        
        result = subprocess.run(
            ["powershell", "-Command", ps_command],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0 and result.stdout:
            try:
                events = json.loads(result.stdout)
                if not isinstance(events, list):
                    events = [events]
                
                for event in events:
                    log_entry = {
                        "timestamp": event.get("TimeGenerated", datetime.now().isoformat()),
                        "source": event.get("Source", "Unknown"),
                        "event_id": event.get("EventID", "N/A"),
                        "message": event.get("Message", ""),
                        "level": event.get("Type", "Information"),
                        "category": category,
                        "os_type": "windows",
                        "host": os.environ.get("COMPUTERNAME", "Unknown")
                    }
                    logs.append(log_entry)
            except json.JSONDecodeError:
                pass
    except Exception as e:
        print(f"[!] Error parsing Windows logs for {category}: {str(e)}")
    
    return logs

def collect_windows_logs(base_path):
    """Collect Windows event logs and store as JSON"""
    all_logs = []
    
    for log, folder in LOG_MAP.items():
        try:
            logs = parse_windows_logs(log.replace(".evtx", ""), folder)
            all_logs.extend(logs)
            
            # Save logs to JSON file
            log_file = os.path.join(base_path, folder, f"{folder}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
            if logs:
                with open(log_file, 'w', encoding='utf-8') as f:
                    for log in logs:
                        f.write(json.dumps(log) + '\n')
                print(f"[+] Collected {len(logs)} logs from {folder}")
        except PermissionError:
            print(f"[!] Permission denied accessing {folder}")
        except Exception as e:
            print(f"[!] Error collecting {folder}: {str(e)}")

