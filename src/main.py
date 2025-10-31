import cv2
import time
import sys
import os
from datetime import datetime, timedelta

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.settings import CAMERAS, DETECTION_CONFIG
from utils.video_utils import VideoHandler
from src.detector import AdvancedPersonDetector
from utils.logger import AlertLogger
from utils.notifier import EmailNotifier
from utils.sms_notifier import SMSNotifier
from src.pose_analyzer import SuspiciousAction


class DSTPSCore:
    def __init__(self):
        self.detector = AdvancedPersonDetector(
            min_detection_confidence=DETECTION_CONFIG.min_detection_confidence,
            enable_pose_analysis=DETECTION_CONFIG.pose_detection_enabled
        )
        self.video_handlers = []
        self.alerts = []
        self.logger = AlertLogger()
        self.email_notifier = EmailNotifier()
        self.sms_notifier = SMSNotifier()
        self.alert_cooldowns = {}
        self.alert_cooldown_time = DETECTION_CONFIG.alert_cooldown

    def initialize_cameras(self) -> bool:
        print("📹 Initializing multi-camera system...")
        success_count = 0
        for camera_config in CAMERAS:
            handler = VideoHandler(camera_config.stream_url)
            if handler.start_stream():
                self.video_handlers.append((handler, camera_config))
                print(f"✅ Camera '{camera_config.name}' at {camera_config.location}")
                success_count += 1
            else:
                print(f"❌ Failed: {camera_config.name}")

        print(f"📊 {success_count}/{len(CAMERAS)} cameras initialized")
        return success_count > 0

    def can_send_alert(self, camera_name: str) -> bool:
        """Prevent alert spam with cooldown"""
        now = time.time()
        last_alert = self.alert_cooldowns.get(camera_name, 0)
        return (now - last_alert) >= self.alert_cooldown_time

    def update_cooldown(self, camera_name: str):
        self.alert_cooldowns[camera_name] = time.time()

    def save_alert_image(self, frame, camera_name, alert_type):
        os.makedirs('data/evidence', exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"data/evidence/{camera_name}_{alert_type}_{timestamp}.jpg"
        cv2.imwrite(filename, frame)
        return filename

    def draw_enhanced_detections(self, frame, detections, restricted_zones, camera_name):
        """Draw detections with color coding based on threat level"""
        # Draw restricted zones
        video_handler = VideoHandler("0")
        video_handler.draw_restricted_zones(frame, restricted_zones)

        for detection in detections:
            x1, y1, x2, y2 = detection['bbox']
            pose_analysis = detection.get('pose_analysis', {})
            action = pose_analysis.get('action', SuspiciousAction.NORMAL)
            action_confidence = pose_analysis.get('confidence', 0.0)
            is_breach = detection.get('breach', False)

            # Color coding based on threat level
            if is_breach:
                color = (0, 0, 255)  # Red for zone breach
                status = "ZONE BREACH"
            elif action != SuspiciousAction.NORMAL:
                color = (255, 165, 0)  # Orange for suspicious action
                status = f"SUSPICIOUS: {action.value.upper()}"
            else:
                color = (0, 255, 0)  # Green for normal
                status = "NORMAL"

            # Draw bounding box
            cv2.rectangle(frame, (x1, y1), (x2, y2), color, 3)

            # Draw status text
            cv2.putText(frame, status, (x1, y1 - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)

            # Draw action confidence for suspicious actions
            if action != SuspiciousAction.NORMAL:
                cv2.putText(frame, f"Confidence: {action_confidence:.1%}",
                            (x1, y1 - 40), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)

            # Draw center point
            center_x, center_y = detection['center']
            cv2.circle(frame, (center_x, center_y), 5, (255, 255, 255), -1)

    def process_streams(self):
        print("🚀 Starting Advanced DSTPS System...")
        print("💡 Features: Multi-cam, Pose Analysis, SMS, Web Dashboard")
        print("🎮 Controls: Q=Quit, S=Screenshot, D=Dashboard, R=Reset Alerts")

        while True:
            for handler, camera_config in self.video_handlers:
                frame = handler.read_frame()
                if frame is None:
                    continue

                # Detect people with advanced features
                detections = self.detector.detect(frame)
                alerts_in_frame = []

                for detection in detections:
                    # Zone breach detection
                    is_breach = self.detector.check_restricted_zone_breach(
                        detection, camera_config.restricted_zones
                    )
                    detection['breach'] = is_breach

                    # Suspicious action detection
                    is_suspicious = self.detector.is_suspicious_action(detection)

                    # Check if we should trigger alerts
                    if is_breach or is_suspicious:
                        alerts_in_frame.append(detection)

                        # Only send alerts if cooldown period has passed
                        if self.can_send_alert(camera_config.name):
                            alert_type = "zone_breach" if is_breach else "suspicious_action"
                            action = detection['pose_analysis'].get('action', SuspiciousAction.NORMAL).value

                            # Save evidence image
                            image_path = self.save_alert_image(
                                detection.get('skeleton_image', frame),
                                camera_config.name,
                                alert_type
                            )

                            # Log alert to file system
                            self.logger.log_alert(
                                camera_name=camera_config.name,
                                zone=detection['bbox'],
                                confidence=detection['confidence'],
                                image_path=image_path,
                                alert_type=alert_type,
                                action_type=action,
                                location=camera_config.location,
                                sms_sent=DETECTION_CONFIG.sms_alerts_enabled,
                                email_sent=True
                            )

                            # Send EMAIL alerts to all configured addresses
                            for email in camera_config.alert_emails:
                                self.email_notifier.send_alert(
                                    email,
                                    f"{alert_type.replace('_', ' ').title()} - {action}",
                                    f"Detected at {camera_config.location}. Confidence: {detection['confidence']:.2f}",
                                    image_path
                                )

                            # Send SMS for critical alerts
                            if DETECTION_CONFIG.sms_alerts_enabled:
                                sms_success = self.sms_notifier.send_alert(
                                    camera_name=camera_config.name,
                                    alert_type=alert_type,
                                    location=camera_config.location,
                                    confidence=detection['confidence']
                                )
                                if sms_success:
                                    print(f"📱 SMS alert sent!")

                            # Update cooldown to prevent spam
                            self.update_cooldown(camera_config.name)
                            print(f" {camera_config.name}: {alert_type} - {action}")

                # Draw enhanced visualization on frame
                self.draw_enhanced_detections(frame, detections, camera_config.restricted_zones, camera_config.name)

                # Display camera feed with status information
                active_alerts = len([a for a in self.alerts if not a.get('acknowledged', False)])
                status_text = f"Cam: {camera_config.name} | Alerts: {active_alerts} | Pose: Active"
                cv2.putText(frame, status_text, (10, 30),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

                # Show frame count for performance monitoring
                frame_count = getattr(self, 'frame_count', 0) + 1
                self.frame_count = frame_count
                cv2.putText(frame, f"Frames: {frame_count}", (10, 60),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

                cv2.imshow(f"DSTPS - {camera_config.name}", frame)

            # Enhanced keyboard controls
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
            elif key == ord('s'):
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                cv2.imwrite(f"data/screenshot_{timestamp}.jpg", frame)
                print(f" Screenshot saved: data/screenshot_{timestamp}.jpg")
            elif key == ord('d'):
                print(" Web dashboard feature - run 'python dashboard/app.py' separately")
            elif key == ord('r'):
                self.alert_cooldowns = {}  # Reset all cooldowns
                print(" Alert cooldowns reset")
            elif key == ord('t'):
                # Test SMS manually
                self.sms_notifier.send_alert(
                    camera_name="Test Camera",
                    alert_type="zone_breach",
                    location="Test Location",
                    confidence=0.95
                )

        # Cleanup resources
        for handler, _ in self.video_handlers:
            handler.release()
        cv2.destroyAllWindows()
        print(" Camera resources released")


def main():
    print("🚀 DSTPS - ADVANCED SECURITY SYSTEM")
    print("=" * 60)
    print("   System Features:")
    print("   • Multi-camera monitoring")
    print("   • Pose analysis (climbing, falling, crawling)")
    print("   • Email & SMS alerts")
    print("   • Restricted zone protection")
    print("   • Evidence logging with timestamps")
    print("=" * 60)

    # Initialize the security system
    system = DSTPSCore()

    if not system.initialize_cameras():
        print("❌ Camera initialization failed - no cameras available")
        print("💡 Check camera connections and config/settings.py")
        return

    try:
        # Start the main processing loop
        system.process_streams()
    except KeyboardInterrupt:
        print("\n Shutting down advanced DSTPS...")
    except Exception as e:
        print(f" Unexpected system error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        print("✅ DSTPS Advanced System stopped safely")


if __name__ == "__main__":
    main()