import os
import sys

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

print("\n=== Testing Dry Run Functionality ===")

# Test chunked query
print("Testing chunked query:")
chunked_filter = QueryFilter(
    date_start="2023-01-05",
    date_end="2023-01-06",  # 1 month
    chunk=True,  # Enable chunking
    chunk_size_days=1,
)

print("   Performing dry run for chunked query (1-day chunks)...")
chunked_dry_run = engine.dry_run(chunked_filter)
print(f"\n{chunked_dry_run}")


# Use the unified download_results method for all types
result = engine.download_results(chunked_filter, auto_approve=True)

# Show detailed summary statistics
if result.snow_pits:
    print("\n--- Dataset Summary ---")
    print(f"   Total pits downloaded: {len(result.snow_pits)}")
    print(f"   Was chunked: {result.was_chunked}")

if result.was_chunked and result.chunk_results:
    print(f"   Chunks processed: {len(result.chunk_results)}")
    successful_chunks = sum(
        1 for chunk in result.chunk_results if chunk.get("success", False)
    )
    print(f"   Successful chunks: {successful_chunks}")

# Show download info
if result.download_info:
    print("   Download details:")
    for key, value in result.download_info.items():
        if key not in [
            "saved_files",
            "chunk_results",
            "states_processed",
            "states_failed",
        ]:  # Skip verbose details
            print(f"     {key}: {value}")
