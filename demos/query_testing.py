import os
import sys
from datetime import timedelta

import pandas as pd

sys.path.append("../src")

from snowpylot.query_engine import QueryEngine, QueryFilter

# Environment check
print("=== Environment Check ===")
user = os.environ.get("SNOWPILOT_USER")
password = os.environ.get("SNOWPILOT_PASSWORD")

if user and password:
    print("✅ Environment variables are set!")
    print(f"   SNOWPILOT_USER: {user}")
    print(f"   SNOWPILOT_PASSWORD: {'*' * len(password)}")
else:
    print("❌ Environment variables not set!")
    print("   Please set SNOWPILOT_USER and SNOWPILOT_PASSWORD")

print("\n=== Testing Authentication ===")
engine = QueryEngine()
auth_success = engine.session.authenticate()

if auth_success:
    print("✅ Authentication successful!")
else:
    print("❌ Authentication failed!")
    print("   Check your credentials and try again")

# Set up dates
start_date = "2019-09-01"
end_date = "2020-01-01"
dates = pd.date_range(start_date, end_date)

for date in dates:
    query_filter = QueryFilter(
        date_start=date, date_end=date + timedelta(days=1), state="MT", per_page=100
    )
    # Preview the results
    preview_test = engine.preview_query(query_filter)
    # Download Pits
    result = engine.query_pits(query_filter, auto_approve=True)
