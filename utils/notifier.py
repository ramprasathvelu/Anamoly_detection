import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables
load_dotenv()


class EmailNotifier:
    """
    Working Gmail notifier with proper configuration
    """

    def __init__(self):
        self.smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
        self.port = int(os.getenv('SMTP_PORT', '587'))
        self.email = os.getenv('SMTP_EMAIL')
        self.password = os.getenv('SMTP_PASSWORD')

        print("🔧 Email Notifier Configuration:")
        print(f"   Email: {self.email}")
        print(f"   Server: {self.smtp_server}:{self.port}")

        if not self.email or not self.password:
            print("❌ Email not configured in .env file")
            print("💡 Create .env file with SMTP_EMAIL and SMTP_PASSWORD")
            self.enabled = False
        else:
            self.enabled = True
            print("✅ Email notifier ready!")

    def send_alert(self, to_email: str, subject: str, message: str, image_path: str = None):
        """Send real email alert"""
        if not self.enabled:
            print("❌ Email not enabled - check .env configuration")
            return False

        try:
            print(f" Attempting to send email to {to_email}...")

            # Create message
            msg = MIMEMultipart()
            msg['From'] = self.email
            msg['To'] = to_email
            msg['Subject'] = f"🚨 DSTPS Alert: {subject}"

            # Create email body
            body = f"""
 DSTPS SECURITY ALERT SYSTEM

 ALERT DETAILS:
• Camera: {to_email}
• Incident: {subject}
• Description: {message}
• Timestamp: {self.get_timestamp()}
• Confidence: High

 ACTION REQUIRED:
1. Review the attached evidence
2. Check live camera feed
3. Dispatch security if needed

This is an automated alert from your DSTPS security system.
"""

            msg.attach(MIMEText(body, 'plain'))

            # Attach image if available
            if image_path and os.path.exists(image_path):
                with open(image_path, 'rb') as f:
                    img_data = f.read()
                    img = MIMEImage(img_data, name=os.path.basename(image_path))
                    msg.attach(img)
                print(f"    Attaching evidence: {image_path}")

            # Send email
            print("    Connecting to SMTP server...")
            server = smtplib.SMTP(self.smtp_server, self.port)
            server.starttls()
            print("    Logging in...")
            server.login(self.email, self.password)
            print("    Sending message...")
            server.send_message(msg)
            server.quit()

            print(f"✅ Email successfully sent to {to_email}")
            return True

        except Exception as e:
            print(f"❌ Email failed: {str(e)}")

            # Helpful error messages
            if "535" in str(e):
                print("💡 Gmail Error: Bad credentials")
                print("   • Make sure 2-Factor Authentication is enabled")
                print("   • Use App Password (not your main password)")
                print("   • Check .env file format")
            elif "connection refused" in str(e).lower():
                print("💡 Network Error: Check internet connection")
            else:
                print("💡 Check your .env file and Gmail settings")

            return False

    def get_timestamp(self):
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


# Fallback notifier
class ConsoleNotifier:
    def send_alert(self, to_email: str, subject: str, message: str, image_path: str = None):
        print(f" [CONSOLE] Alert for {to_email}: {subject}")
        return True