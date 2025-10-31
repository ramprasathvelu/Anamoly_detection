import os
import subprocess
import sys


def setup_advanced_dstps():
    print("🚀 Setting up Advanced DSTPS...")

    # Create directory structure
    directories = [
        'dashboard/templates',
        'data/evidence',
        'logs',
        'models'
    ]

    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"✅ Created: {directory}")

    # Install additional requirements
    requirements = [
        'flask',
        'twilio',
        'python-dotenv'
    ]

    for package in requirements:
        try:
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', package])
            print(f"✅ Installed: {package}")
        except:
            print(f"❌ Failed to install: {package}")

    print("\n🎉 Advanced DSTPS Setup Complete!")
    print("📁 New Structure:")
    print("   - Multi-camera support")
    print("   - Pose detection for climbing/falling")
    print("   - Web dashboard (run: python dashboard/app.py)")
    print("   - SMS alerts (configure Twilio in .env)")
    print("   - Enhanced evidence collection")

    print("\n🚀 To start: python run.py")
    print("🌐 Dashboard: python dashboard/app.py")


if __name__ == "__main__":
    setup_advanced_dstps()