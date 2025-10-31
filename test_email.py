from utils.notifier import EmailNotifier


def test_email():
    print("Testing email configuration...")
    notifier = EmailNotifier()

    # Test send
    success = notifier.send_alert(
        " ",  # Send to yourself for testing
        "TEST: DSTPS Email Test",
        "This is a test email from your DSTPS security system. If you receive this, email is working!",
        None  # No image for test
    )

    if success:
        print("🎉 Email test SUCCESS! Check your inbox.")
    else:
        print("❌ Email test failed. Check the error messages above.")


if __name__ == "__main__":
    test_email()