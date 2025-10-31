from utils.sms_notifier import SMSNotifier


def test_sms_alert():
    print("📱 Testing SMS Alert System...")

    sms = SMSNotifier()

    if sms.enabled:
        print("🚀 Sending test security alert...")
        success = sms.send_alert(
            camera_name="Main Entrance",
            alert_type="zone_breach",
            location="Building A - Front Door",
            confidence=0.92
        )

        if success:
            print("🎉 Check your phone! SMS should arrive within 30 seconds.")
        else:
            print("❌ SMS test failed. Check your Twilio credentials.")
    else:
        print("💡 Configure Twilio in .env file to enable SMS")


if __name__ == "__main__":
    test_sms_alert()
