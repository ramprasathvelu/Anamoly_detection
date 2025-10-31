import os
from twilio.rest import Client
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()


class SMSNotifier:
    def __init__(self):
        self.account_sid = os.getenv('TWILIO_ACCOUNT_SID')
        self.auth_token = os.getenv('TWILIO_AUTH_TOKEN')
        self.twilio_number = os.getenv('TWILIO_PHONE_NUMBER')
        self.your_number = os.getenv('YOUR_PHONE_NUMBER')

        print("📱 SMS Notifier Status:")
        print(f"   Account SID: {'✅ Found' if self.account_sid else '❌ Missing'}")
        print(f"   Auth Token: {'✅ Found' if self.auth_token else '❌ Missing'}")
        print(f"   Twilio Number: {'✅ ' + self.twilio_number if self.twilio_number else '❌ Missing'}")
        print(f"   Your Number: {'✅ ' + self.your_number if self.your_number else '❌ Missing'}")

        # Check if all credentials are present
        if all([self.account_sid, self.auth_token, self.twilio_number, self.your_number]):
            try:
                self.client = Client(self.account_sid, self.auth_token)
                self.enabled = True
                print("✅ SMS Notifier Ready - Real SMS Enabled!")
            except Exception as e:
                print(f"❌ Twilio setup failed: {e}")
                self.enabled = False
        else:
            self.enabled = False
            print("🔶 SMS Simulation Mode - Configure .env for real SMS")

    def send_alert(self, camera_name: str, alert_type: str, location: str, confidence: float):
        """Send SMS alert (real or simulation)"""
        message_body = self._create_message(camera_name, alert_type, location, confidence)

        if self.enabled:
            try:
                # Send REAL SMS
                message = self.client.messages.create(
                    body=message_body,
                    from_=self.twilio_number,
                    to=self.your_number
                )
                print(f"✅ REAL SMS Sent to {self.your_number}")
                print(f"   Message: {message_body}")
                return True
            except Exception as e:
                print(f"❌ Real SMS failed: {e}")
                # Fall back to simulation
                return self._simulate_sms(message_body)
        else:
            # Simulation mode
            return self._simulate_sms(message_body)

    def _simulate_sms(self, message_body: str) -> bool:
        """Show what SMS would look like"""
        print("📱 [SMS SIMULATION]")
        print("   " + "=" * 40)
        for line in message_body.split('\n'):
            print(f"   {line}")
        print("   " + "=" * 40)
        print("   💡 Configure Twilio in .env for real SMS")
        return True

    def _create_message(self, camera_name: str, alert_type: str, location: str, confidence: float) -> str:
        """Create formatted SMS message"""
        emoji_map = {
            "zone_breach": "🚨",
            "suspicious_action": "⚠️",
            "climbing": "🧗",
            "falling": "🆘",
            "crawling": "🕵️"
        }

        emoji = emoji_map.get(alert_type, "🚨")

        if alert_type == "zone_breach":
            return f"""{emoji} DSTPS SECURITY ALERT {emoji}

INTRUDER DETECTED!
📍 {location}
📷 {camera_name}
🕒 {self._get_timestamp()}

IMMEDIATE ACTION REQUIRED"""

        else:
            return f"""{emoji} SUSPICIOUS ACTIVITY {emoji}

{alert_type.upper()} DETECTED
📍 {location}
📷 {camera_name}
🎯 Confidence: {confidence:.0%}
🕒 {self._get_timestamp()}"""

    def _get_timestamp(self):
        return datetime.now().strftime("%H:%M:%S")


# Test function
def test_sms():
    sms = SMSNotifier()
    print("\n Testing SMS...")
    sms.send_alert(
        camera_name="Main Entrance",
        alert_type="zone_breach",
        location="Building A - Front Door",
        confidence=0.95
    )


if __name__ == "__main__":
    test_sms()