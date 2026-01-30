import time
import json
from datetime import datetime
import os
from agent.os_detector import detect_os
from agent.folder_manager import create_folders
from agent.windows_logs import collect_windows_logs
from agent.linux_logs import collect_linux_logs
from agent.config import COLLECTION_INTERVAL, DEBUG, LOG_INDEX_FILE, SHUTDOWN_SIGNAL_FILE

def init_index():
    """Initialize log index file"""
    os.makedirs(os.path.dirname(LOG_INDEX_FILE), exist_ok=True)
    if not os.path.exists(LOG_INDEX_FILE):
        with open(LOG_INDEX_FILE, 'w') as f:
            pass

def add_to_index(log_entry):
    """Add log entry to index"""
    try:
        with open(LOG_INDEX_FILE, 'a', encoding='utf-8') as f:
            f.write(json.dumps(log_entry) + '\n')
    except Exception as e:
        if DEBUG:
            print(f"[!] Error adding to index: {str(e)}")

def check_shutdown_signal():
    """Check if shutdown signal file exists"""
    if os.path.exists(SHUTDOWN_SIGNAL_FILE):
        try:
            os.remove(SHUTDOWN_SIGNAL_FILE)
            print("[+] Shutdown signal received from dashboard")
            return True
        except Exception as e:
            print(f"[!] Error removing shutdown signal: {str(e)}")
            return True
    return False

def run():
    os_type = detect_os()
    if os_type == "unsupported":
        print("[!] Unsupported operating system")
        return

    base_path = create_folders(os_type)
    init_index()
    
    print(f"[+] UniLogX Agent started on {os_type.upper()}")
    print(f"[+] Log directory: {base_path}")
    print(f"[+] Collection interval: {COLLECTION_INTERVAL}s")

    try:
        while True:
            # Check for shutdown signal from dashboard
            if check_shutdown_signal():
                break
                
            try:
                if DEBUG:
                    print(f"[*] Collecting logs at {datetime.now().isoformat()}")
                
                if os_type == "windows":
                    collect_windows_logs(base_path)
                else:
                    collect_linux_logs(base_path)

                time.sleep(COLLECTION_INTERVAL)
            except KeyboardInterrupt:
                print("[+] Collection paused")
                time.sleep(1)
            except Exception as e:
                print(f"[!] Error during collection: {str(e)}")
                time.sleep(COLLECTION_INTERVAL)
    except KeyboardInterrupt:
        print("[+] UniLogX Agent stopped")

if __name__ == "__main__":
    run()


