#!/usr/bin/env python3
"""
Complete setup and test script for snowpylot
This script handles environment setup and tests all functionality
"""

import os
import sys


def setup_environment():
    """Set up environment variables"""
    print("=== Setting up Environment ===")

    # Method 1: Try to load from .env file
    try:
        from dotenv import load_dotenv

        load_dotenv()
        print("✅ Loaded .env file")

        user = os.environ.get("SNOWPILOT_USER")
        password = os.environ.get("SNOWPILOT_PASSWORD")

        if user and password and password != "YOUR_PASSWORD_HERE":
            print(f"✅ Environment variables loaded from .env file")
            print(f"   SNOWPILOT_USER: {user}")
            print(f"   SNOWPILOT_PASSWORD: {'*' * len(password)}")
            return True
        else:
            print("⚠️  .env file exists but credentials not properly set")

    except ImportError:
        print("⚠️  python-dotenv not available")
    except Exception as e:
        print(f"⚠️  Could not load .env file: {e}")

    # Method 2: Check system environment variables
    user = os.environ.get("SNOWPILOT_USER")
    password = os.environ.get("SNOWPILOT_PASSWORD")

    if user and password:
        print("✅ Using system environment variables")
        print(f"   SNOWPILOT_USER: {user}")
        print(f"   SNOWPILOT_PASSWORD: {'*' * len(password)}")
        return True

    # Method 3: Manual setup instructions
    print("\n❌ No credentials found!")
    print("\nPlease set up your credentials using ONE of these methods:")
    print("\n1. Edit the .env file:")
    print("   SNOWPILOT_USER=katisthebatis")
    print("   SNOWPILOT_PASSWORD=your_actual_password")

    print("\n2. Set environment variables in your shell:")
    print("   export SNOWPILOT_USER='katisthebatis'")
    print("   export SNOWPILOT_PASSWORD='your_actual_password'")

    print("\n3. Set them directly in this script (uncomment and edit):")
    print("   # os.environ['SNOWPILOT_USER'] = 'katisthebatis'")
    print("   # os.environ['SNOWPILOT_PASSWORD'] = 'your_actual_password'")

    # Uncomment and edit these lines to set credentials directly:
    # os.environ['SNOWPILOT_USER'] = 'katisthebatis'
    # os.environ['SNOWPILOT_PASSWORD'] = 'your_actual_password'

    return False


def test_imports():
    """Test that all required modules can be imported"""
    print("\n=== Testing Imports ===")

    try:
        import pandas as pd

        print("✅ pandas imported successfully")
    except ImportError as e:
        print(f"❌ pandas import failed: {e}")
        return False

    try:
        import snowpylot

        print("✅ snowpylot imported successfully")
    except ImportError as e:
        print(f"❌ snowpylot import failed: {e}")
        print("   Run: pip install -e .")
        return False

    try:
        from snowpylot.query_engine import QueryEngine, QueryFilter, SnowPilotSession

        print("✅ Query engine components imported successfully")
    except ImportError as e:
        print(f"❌ Query engine import failed: {e}")
        return False

    try:
        from snowpylot.query_engine import (
            preview_by_date_range,
            query_by_date_range,
            query_by_pit_id,
            query_by_organization,
            query_by_location,
        )

        print("✅ Convenience functions imported successfully")
    except ImportError as e:
        print(f"❌ Convenience functions import failed: {e}")
        return False

    return True


def test_authentication():
    """Test authentication with snowpilot.org"""
    print("\n=== Testing Authentication ===")

    try:
        from snowpylot.query_engine import SnowPilotSession

        session = SnowPilotSession()

        if session.authenticate():
            print("✅ Authentication successful!")
            return True
        else:
            print("❌ Authentication failed")
            print("   Check your credentials and network connection")
            return False

    except Exception as e:
        print(f"❌ Authentication error: {e}")
        return False


def test_basic_functionality():
    """Test basic query engine functionality"""
    print("\n=== Testing Basic Functionality ===")

    try:
        from snowpylot.query_engine import QueryEngine, QueryFilter
        from datetime import datetime, timedelta

        # Initialize query engine
        engine = QueryEngine(pits_path="data/test_downloads")
        print("✅ Query engine initialized")

        # Test preview functionality
        today = datetime.now()
        start_date = (today - timedelta(days=7)).strftime("%Y-%m-%d")
        end_date = today.strftime("%Y-%m-%d")

        query_filter = QueryFilter(date_start=start_date, date_end=end_date, state="MT")

        print(f"✅ Query filter created: {start_date} to {end_date}, MT")

        # Test preview
        preview = engine.preview_query(query_filter)
        print(f"✅ Preview successful: {preview.estimated_count} pits estimated")

        return True

    except Exception as e:
        print(f"❌ Basic functionality test failed: {e}")
        return False


def main():
    """Main function to run all tests"""
    print("🏔️  SNOWPYLOT SETUP AND TEST SCRIPT")
    print("=" * 50)

    # Test 1: Environment setup
    env_ok = setup_environment()

    # Test 2: Imports
    imports_ok = test_imports()

    if not imports_ok:
        print("\n❌ Setup incomplete - fix import issues first")
        return False

    # Test 3: Authentication (only if environment is set up)
    auth_ok = False
    if env_ok:
        auth_ok = test_authentication()
    else:
        print("\n⚠️  Skipping authentication test - no credentials")

    # Test 4: Basic functionality (only if authenticated)
    func_ok = False
    if auth_ok:
        func_ok = test_basic_functionality()
    else:
        print("\n⚠️  Skipping functionality test - not authenticated")

    # Summary
    print("\n" + "=" * 50)
    print("SETUP SUMMARY")
    print("=" * 50)
    print(f"Environment: {'✅ OK' if env_ok else '❌ NEEDS SETUP'}")
    print(f"Imports: {'✅ OK' if imports_ok else '❌ FAILED'}")
    print(
        f"Authentication: {'✅ OK' if auth_ok else '❌ FAILED' if env_ok else '⚠️  SKIPPED'}"
    )
    print(
        f"Basic functionality: {'✅ OK' if func_ok else '❌ FAILED' if auth_ok else '⚠️  SKIPPED'}"
    )

    if env_ok and imports_ok and auth_ok and func_ok:
        print("\n🎉 All tests passed! Your snowpylot setup is complete!")
        print("\nYou can now run your notebook or use the query engine.")
        return True
    else:
        print("\n❌ Some tests failed. Please fix the issues above.")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
