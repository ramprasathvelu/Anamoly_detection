import json
import csv
import time
import os
from datetime import datetime
from typing import Dict, Any, List


class AlertLogger:
    def __init__(self, log_file: str = "data/alerts.json", csv_file: str = "data/alerts.csv"):
        self.log_file = log_file
        self.csv_file = csv_file
        self.setup_logging()
        self.alert_count = 0

    def setup_logging(self):
        """Create log files and directories"""
        os.makedirs('data', exist_ok=True)

        # Initialize JSON log file
        if not os.path.exists(self.log_file):
            with open(self.log_file, 'w') as f:
                json.dump({"alerts": [], "system_info": {"version": "2.0", "created": self.get_timestamp()}}, f)

        # Initialize CSV log file with enhanced headers
        if not os.path.exists(self.csv_file):
            with open(self.csv_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow([
                    'alert_id', 'timestamp', 'camera_name', 'location',
                    'alert_type', 'action_type', 'confidence',
                    'zone_coordinates', 'image_path', 'sms_sent', 'email_sent'
                ])

    def log_alert(self, camera_name: str, zone: tuple, confidence: float,
                  image_path: str = "", alert_type: str = "zone_breach",
                  action_type: str = "normal", location: str = "Unknown Location",
                  sms_sent: bool = False, email_sent: bool = True):
        """Enhanced alert logging with all new parameters"""
        self.alert_count += 1
        alert_id = f"ALT{self.alert_count:06d}"
        timestamp = self.get_timestamp()

        alert_data = {
            'alert_id': alert_id,
            'timestamp': timestamp,
            'camera_name': camera_name,
            'location': location,
            'alert_type': alert_type,
            'action_type': action_type,
            'confidence': confidence,
            'zone_coordinates': str(zone),
            'image_path': image_path,
            'sms_sent': sms_sent,
            'email_sent': email_sent
        }

        # Log to JSON
        self._log_to_json(alert_data)

        # Log to CSV
        self._log_to_csv(alert_data)

        print(f" Alert {alert_id} logged: {camera_name} - {alert_type} - {action_type}")
        return alert_id

    def _log_to_json(self, alert_data: Dict[str, Any]):
        """Log alert to JSON file"""
        try:
            with open(self.log_file, 'r+', encoding='utf-8') as f:
                data = json.load(f)
                data['alerts'].append(alert_data)
                f.seek(0)
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"❌ JSON log error: {e}")

    def _log_to_csv(self, alert_data: Dict[str, Any]):
        """Log alert to CSV file"""
        try:
            with open(self.csv_file, 'a', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow([
                    alert_data['alert_id'],
                    alert_data['timestamp'],
                    alert_data['camera_name'],
                    alert_data['location'],
                    alert_data['alert_type'],
                    alert_data['action_type'],
                    alert_data['confidence'],
                    alert_data['zone_coordinates'],
                    alert_data['image_path'],
                    alert_data['sms_sent'],
                    alert_data['email_sent']
                ])
        except Exception as e:
            print(f"❌ CSV log error: {e}")

    def get_recent_alerts(self, limit: int = 10) -> List[Dict]:
        """Get recent alerts for dashboard"""
        try:
            with open(self.log_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data['alerts'][-limit:]
        except:
            return []

    def get_alert_stats(self) -> Dict[str, Any]:
        """Get alert statistics"""
        try:
            with open(self.log_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                alerts = data['alerts']

                stats = {
                    'total_alerts': len(alerts),
                    'today_alerts': len(
                        [a for a in alerts if a['timestamp'].startswith(datetime.now().strftime("%Y-%m-%d"))]),
                    'zone_breaches': len([a for a in alerts if a['alert_type'] == 'zone_breach']),
                    'suspicious_actions': len([a for a in alerts if a['alert_type'] == 'suspicious_action']),
                    'sms_sent': len([a for a in alerts if a['sms_sent']]),
                    'emails_sent': len([a for a in alerts if a['email_sent']])
                }
                return stats
        except:
            return {'total_alerts': 0, 'today_alerts': 0, 'zone_breaches': 0,
                    'suspicious_actions': 0, 'sms_sent': 0, 'emails_sent': 0}

    def get_timestamp(self):
        return datetime.now().isoformat()


# Test the logger
if __name__ == "__main__":
    logger = AlertLogger()

    # Test log
    test_id = logger.log_alert(
        camera_name="Test Camera",
        zone=(100, 100, 400, 400),
        confidence=0.85,
        image_path="data/test_alert.jpg",
        alert_type="zone_breach",
        action_type="climbing",
        location="Test Location",
        sms_sent=True,
        email_sent=True
    )

    print(f"✅ Test alert logged: {test_id}")
    print(f" Stats: {logger.get_alert_stats()}")