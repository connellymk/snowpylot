import os
import sys
import time
from datetime import datetime, timedelta

sys.path.append("../src")

from snowpylot.query_engine import QueryEngine, QueryFilter

# Environment check
print("=== Environment Check ===")
# Set environment variables with hardcoded credentials
os.environ["SNOWPILOT_USER"] = "katisthebatis"
os.environ["SNOWPILOT_PASSWORD"] = "mkconn123"

user = os.environ.get("SNOWPILOT_USER")
password = os.environ.get("SNOWPILOT_PASSWORD")

if user and password:
    print("✅ Environment variables are set!")
    print(f"   SNOWPILOT_USER: {user}")
    print(f"   SNOWPILOT_PASSWORD: {'*' * len(password)}")
else:
    print("❌ Environment variables not set!")
    print("   Please set SNOWPILOT_USER and SNOWPILOT_PASSWORD")
    sys.exit(1)

print("\n=== Setting Up Download Location ===")
# Ask user for custom download location
default_path = "data/snowpits"
custom_path = input(
    f"Enter download folder path (press Enter for default: {default_path}): "
).strip()

if custom_path:
    download_path = custom_path
    print(f"✅ Using custom download path: {download_path}")
else:
    download_path = default_path
    print(f"✅ Using default download path: {download_path}")

# Show absolute path for clarity
try:
    abs_path = os.path.abspath(download_path)
    print(f"   Absolute path: {abs_path}")
except Exception as e:
    print(f"   Warning: Could not determine absolute path: {e}")

print("\n=== Testing Authentication ===")
engine = QueryEngine(pits_path=download_path)
auth_success = engine.session.authenticate()

if auth_success:
    print("✅ Authentication successful!")
else:
    print("❌ Authentication failed!")
    print("   Check your credentials and try again")
    sys.exit(1)

print("\n=== Manual Chunking Example ===")
print(
    "Demonstrating manual chunking with controlled delays to work around "
    "API caching bug"
)

# Define date range to chunk manually
start_date = datetime.strptime(
    "2022-05-16", "%Y-%m-%d"
)  # 2015-09-01, 2016-01-04, 2018-12-11
end_date = datetime.strptime("2025-08-22", "%Y-%m-%d")

current_date = start_date
while current_date < end_date:
    # Use single-day query (start_date = end_date)
    # The query engine will automatically add +1 day to end_date,
    # so this will fetch exactly one day of data
    query_filter = QueryFilter(
        date_start=current_date.strftime("%Y-%m-%d"),
        date_end=current_date.strftime("%Y-%m-%d"),  # Same as start_date
    )

    print(f"Downloading data for: {current_date.strftime('%Y-%m-%d')}")
    result = engine.download_results(query_filter, auto_approve=True)

    # Move to next day
    current_date = current_date + timedelta(days=1)

    # add a delay of 60 seconds to work around API caching and rate limiting
    time.sleep(5)
