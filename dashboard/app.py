from flask import Flask, render_template, jsonify, Response, send_file
import json
import os
import cv2
from datetime import datetime
import glob

app = Flask(__name__)


class DashboardManager:
    def __init__(self):
        self.alert_file = "data/alerts.json"
        self.evidence_dir = "data/evidence/"

    def get_alerts(self):
        """Get all alerts from JSON file"""
        try:
            with open(self.alert_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get('alerts', [])
        except:
            return []

    def get_stats(self):
        """Get comprehensive statistics"""
        alerts = self.get_alerts()
        now = datetime.now()
        today_str = now.strftime("%Y-%m-%d")

        # Calculate various statistics
        stats = {
            'total_alerts': len(alerts),
            'today_alerts': len([a for a in alerts if a.get('timestamp', '').startswith(today_str)]),
            'zone_breaches': len([a for a in alerts if a.get('alert_type') == 'zone_breach']),
            'suspicious_actions': len([a for a in alerts if a.get('alert_type') == 'suspicious_action']),
            'active_cameras': 1,  # You can expand this
            'system_uptime': 'Running',
            'last_alert': alerts[-1] if alerts else None
        }

        # Alert breakdown by type
        alert_types = {}
        for alert in alerts:
            alert_type = alert.get('alert_type', 'unknown')
            alert_types[alert_type] = alert_types.get(alert_type, 0) + 1

        stats['alert_breakdown'] = alert_types
        return stats

    def get_recent_evidence(self, limit=6):
        """Get recent evidence images"""
        try:
            image_files = glob.glob(os.path.join(self.evidence_dir, "*.jpg"))
            # Sort by modification time (newest first)
            image_files.sort(key=os.path.getmtime, reverse=True)
            return image_files[:limit]
        except:
            return []


dashboard = DashboardManager()


@app.route('/')
def index():
    """Main dashboard page"""
    return render_template('index.html')


@app.route('/api/alerts')
def api_alerts():
    """API endpoint for alerts"""
    alerts = dashboard.get_alerts()
    # Return latest 20 alerts
    return jsonify(alerts[-20:][::-1])  # Reverse to show newest first


@app.route('/api/stats')
def api_stats():
    """API endpoint for statistics"""
    return jsonify(dashboard.get_stats())


@app.route('/api/evidence')
def api_evidence():
    """API endpoint for recent evidence"""
    evidence = dashboard.get_recent_evidence()
    evidence_data = []

    for img_path in evidence:
        if os.path.exists(img_path):
            filename = os.path.basename(img_path)
            # Extract info from filename: CameraName_AlertType_Timestamp.jpg
            parts = filename.replace('.jpg', '').split('_')
            camera_name = parts[0] if len(parts) > 0 else 'Unknown'
            alert_type = parts[1] if len(parts) > 1 else 'unknown'
            timestamp = parts[2] if len(parts) > 2 else ''

            evidence_data.append({
                'path': img_path,
                'filename': filename,
                'camera': camera_name,
                'type': alert_type,
                'timestamp': timestamp
            })

    return jsonify(evidence_data)


@app.route('/evidence/<filename>')
def serve_evidence(filename):
    """Serve evidence images"""
    return send_file(f"data/evidence/{filename}")


@app.route('/api/alert/<alert_id>/acknowledge', methods=['POST'])
def acknowledge_alert(alert_id):
    """Acknowledge an alert"""
    # In a real system, you'd update the alert status in database
    return jsonify({'status': 'success', 'alert_id': alert_id})


# Live camera feed (optional)
@app.route('/video_feed')
def video_feed():
    """Live camera feed (placeholder)"""

    def generate():
        camera = cv2.VideoCapture(0)
        while True:
            success, frame = camera.read()
            if not success:
                break
            else:
                ret, buffer = cv2.imencode('.jpg', frame)
                frame_bytes = buffer.tobytes()
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
        camera.release()

    return Response(generate(), mimetype='multipart/x-mixed-replace; boundary=frame')


if __name__ == '__main__':
    # Create necessary directories
    os.makedirs('dashboard/templates', exist_ok=True)
    os.makedirs('data/evidence', exist_ok=True)

    print("🌐 Starting DSTPS Dashboard...")
    print("📊 Dashboard URL: http://localhost:5000")
    print("📊 Statistics: http://localhost:5000/api/stats")
    print("🚨 Alerts API: http://localhost:5000/api/alerts")
    print("📸 Evidence API: http://localhost:5000/api/evidence")

    app.run(debug=True, host='0.0.0.0', port=5000)