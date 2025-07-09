#!/usr/bin/env python3
"""
Secure credential setup for SnowPilot
This script helps you set up environment variables for secure credential storage
"""

import os
import getpass
from pathlib import Path


def setup_environment_variables():
    """Set up environment variables for SnowPilot credentials"""

    print("=== SnowPilot Credential Setup ===")
    print(
        "This will help you securely store your SnowPilot credentials as environment variables.\n"
    )

    # Get current values
    current_user = os.environ.get("SNOWPILOT_USER")
    current_pass = os.environ.get("SNOWPILOT_PASSWORD")

    if current_user and current_pass:
        print(f"Current credentials found:")
        print(f"  SNOWPILOT_USER: {current_user}")
        print(f"  SNOWPILOT_PASSWORD: {'*' * len(current_pass)}")

        update = input("\nUpdate these credentials? (y/n): ").lower().strip()
        if update != "y":
            print("Keeping existing credentials.")
            return True

    # Get credentials
    print("\nEnter your SnowPilot credentials:")
    username = input("Username: ").strip()
    password = getpass.getpass("Password: ")

    if not username or not password:
        print("❌ Both username and password are required!")
        return False

    # Determine shell type
    shell = os.environ.get("SHELL", "/bin/bash")
    if "zsh" in shell:
        profile_file = Path.home() / ".zshrc"
    elif "bash" in shell:
        profile_file = Path.home() / ".bashrc"
    else:
        profile_file = Path.home() / ".profile"

    # Create the export commands
    export_commands = [
        f'export SNOWPILOT_USER="{username}"',
        f'export SNOWPILOT_PASSWORD="{password}"',
    ]

    print(f"\n=== Adding to {profile_file} ===")

    # Check if variables already exist in the file
    if profile_file.exists():
        content = profile_file.read_text()
        if "SNOWPILOT_USER" in content:
            print("⚠️  SNOWPILOT_USER already exists in your profile file.")
            replace = input("Replace existing entries? (y/n): ").lower().strip()
            if replace == "y":
                # Remove existing entries
                lines = content.split("\n")
                lines = [
                    line
                    for line in lines
                    if not line.strip().startswith("export SNOWPILOT_")
                ]
                content = "\n".join(lines)
                profile_file.write_text(content)

    # Append new variables
    with open(profile_file, "a") as f:
        f.write("\n# SnowPilot Credentials\n")
        for cmd in export_commands:
            f.write(f"{cmd}\n")

    print(f"✅ Environment variables added to {profile_file}")
    print(f"\nTo use them immediately, run:")
    print(f"  source {profile_file}")
    print(f"Or start a new terminal session.")

    # Test the setup
    print("\n=== Testing Setup ===")
    # Set for current session
    os.environ["SNOWPILOT_USER"] = username
    os.environ["SNOWPILOT_PASSWORD"] = password

    try:
        from snowpylot.query_engine import SnowPilotSession

        session = SnowPilotSession()
        if session.authenticate():
            print("✅ Authentication successful!")
            return True
        else:
            print("❌ Authentication failed. Please check your credentials.")
            return False
    except Exception as e:
        print(f"❌ Error testing credentials: {e}")
        return False


def show_usage_example():
    """Show how to use the environment variables in code"""
    print("\n=== Usage in Your Code ===")
    print("Here's how to access your credentials securely in Python:")
    print("""
import os

# Get credentials from environment variables
username = os.environ.get("SNOWPILOT_USER")
password = os.environ.get("SNOWPILOT_PASSWORD")

# Check if credentials are available
if not username or not password:
    raise ValueError("SNOWPILOT_USER and SNOWPILOT_PASSWORD environment variables must be set")

# Use with SnowPilot
from snowpylot.query_engine import QueryEngine
engine = QueryEngine()
# Authentication happens automatically using the environment variables
""")


if __name__ == "__main__":
    success = setup_environment_variables()
    if success:
        show_usage_example()
    else:
        print("\n❌ Setup failed. Please try again.")
