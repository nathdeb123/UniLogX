"""
Alert Module - Similar to Elasticsearch Alerting
Detects critical events and patterns
"""
import json
from datetime import datetime, timedelta
from collections import defaultdict

class AlertManager:
    def __init__(self):
        self.alerts = []
        self.critical_patterns = {
            'ERROR': 3,           # 3+ errors in 5 minutes
            'CRITICAL': 1,        # Any critical error
            'PermissionError': 2, # 2+ permission errors
            'Timeout': 2,         # 2+ timeout errors
        }
    
    def check_alert(self, log_entry):
        """Check if log triggers an alert"""
        level = log_entry.get('level', '').upper()
        message = log_entry.get('message', '').upper()
        
        # Critical level always triggers alert
        if level == 'CRITICAL':
            return self.create_alert(log_entry, 'CRITICAL', 'Critical log detected')
        
        # Check for patterns
        for pattern, threshold in self.critical_patterns.items():
            if pattern.upper() in message or pattern.upper() in level:
                return self.create_alert(
                    log_entry, 
                    'WARNING', 
                    f'Pattern detected: {pattern}'
                )
        
        return None
    
    def create_alert(self, log_entry, severity, reason):
        """Create an alert object"""
        alert = {
            'timestamp': datetime.now().isoformat(),
            'severity': severity,
            'reason': reason,
            'source_log': log_entry,
            'id': hash(json.dumps(log_entry)) % 10**8
        }
        self.alerts.append(alert)
        return alert
    
    def get_recent_alerts(self, minutes=60):
        """Get recent alerts within specified minutes"""
        cutoff = datetime.now() - timedelta(minutes=minutes)
        
        return [
            alert for alert in self.alerts
            if datetime.fromisoformat(alert['timestamp']) > cutoff
        ]
