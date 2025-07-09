#!/usr/bin/env python3
"""
Test script for snowpylot setup
This script will test your environment setup and credentials
"""

import os
import sys


def test_environment():
    """Test environment variables and imports"""

    print("=== SnowPilot Setup Test ===\n")

    # Try to load from .env file first
    try:
        from dotenv import load_dotenv

        load_dotenv()
        print("✅ Loaded .env file")
    except ImportError:
        print("⚠️  python-dotenv not installed. Install with: pip install python-dotenv")
        print("    Using system environment variables instead")
    except Exception as e:
        print(f"⚠️  Could not load .env file: {e}")
        print("    Using system environment variables instead")

    # Test environment variables
    print("\n=== Environment Check ===")
    user = os.environ.get("SNOWPILOT_USER")
    password = os.environ.get("SNOWPILOT_PASSWORD")

    if user and password:
        print("✅ Environment variables are set!")
        print(f"   SNOWPILOT_USER: {user}")
        print(f"   SNOWPILOT_PASSWORD: {'*' * len(password)}")
    else:
        print("❌ Environment variables not set!")
        print("Please set them in your .env file:")
        print("   SNOWPILOT_USER=your_username")
        print("   SNOWPILOT_PASSWORD=your_password")
        print("\nOr set them manually:")
        print('   export SNOWPILOT_USER="your_username"')
        print('   export SNOWPILOT_PASSWORD="your_password"')
        print("\nOr set them in this script:")
        print('   os.environ["SNOWPILOT_USER"] = "your_username"')
        print('   os.environ["SNOWPILOT_PASSWORD"] = "your_password"')

        # Uncomment and fill in these lines if you want to set them directly:
        # os.environ['SNOWPILOT_USER'] = 'katisthebatis'
        # os.environ['SNOWPILOT_PASSWORD'] = 'YOUR_PASSWORD_HERE'

        return False

    # Test imports
    print("\n=== Imports ===")
    try:
        import pandas as pd

        print("✅ pandas imported successfully")

        import snowpylot

        print("✅ snowpylot imported successfully")

        from snowpylot.query_engine import SnowPilotSession

        print("✅ SnowPilotSession imported successfully")

    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Make sure to install snowpylot: pip install -e .")
        return False

    # Test authentication
    print("\n=== Testing Authentication ===")
    try:
        session = SnowPilotSession()
        if session.authenticate():
            print("✅ Authentication successful!")
            return True
        else:
            print("❌ Authentication failed - please check your credentials")
            return False
    except Exception as e:
        print(f"❌ Authentication error: {e}")
        return False


if __name__ == "__main__":
    success = test_environment()
    if success:
        print("\n🎉 All tests passed! Your snowpylot setup is ready to use.")
    else:
        print("\n❌ Setup incomplete. Please fix the issues above.")
        sys.exit(1)
