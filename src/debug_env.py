import os
from dotenv import load_dotenv

print("🔍 Debugging .env file loading...")

# Get current directory
current_dir = os.getcwd()
print(f"Current directory: {current_dir}")

# List files in current directory
print("Files in current directory:")
for file in os.listdir('.'):
    print(f"  - {file}")

# Try to load .env
load_dotenv()

# Check if variables are loaded
email = os.getenv('SMTP_EMAIL')
password = os.getenv('SMTP_PASSWORD')

print(f"SMTP_EMAIL: {email}")
print(f"SMTP_PASSWORD: {'*' * len(password) if password else 'Not found'}")

if not email or not password:
    print("❌ .env file not loaded properly")
    print("💡 Make sure .env file exists in the same folder as this script")
else:
    print("✅ .env file loaded successfully!")