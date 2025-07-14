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

print("\n=== Testing Authentication ===")
engine = QueryEngine()
auth_success = engine.session.authenticate()

if auth_success:
    print("✅ Authentication successful!")
else:
    print("❌ Authentication failed!")
    print("   Check your credentials and try again")
    sys.exit(1)

print("\n=== Testing Dry Run Functionality ===")

# Create query filter with 1-week chunking
query_filter = QueryFilter(
    date_start="2023-01-01",
    date_end="2023-01-31",
    # state="MT",
    chunk=True,  # Enable chunking
    chunk_size_days=7,
)

# Perform dry run to see what would be downloaded
print("Performing dry run...")
dry_run_result = engine.dry_run(query_filter)
print(f"\n{dry_run_result}")

print("\n=== Testing Large Dataset Download ===")

# Ask user if they want to proceed with the actual download
if dry_run_result.total_estimated_pits > 0:
    proceed = (
        input(
            f"\nDo you want to proceed with downloading {dry_run_result.total_estimated_pits} pits? (y/N): "
        )
        .lower()
        .strip()
    )

    if proceed in ["y", "yes"]:
        print("Starting download...")
        result = engine.query_pits(query_filter, auto_approve=True)

        # Show summary statistics
        if result.snow_pits:
            print("\n--- Dataset Summary ---")
            print(f"   Total pits: {len(result.snow_pits)}")

            # Group by state
            states = {}
            for pit in result.snow_pits:
                if pit.core_info.location and pit.core_info.location.region:
                    state = pit.core_info.location.region
                    states[state] = states.get(state, 0) + 1
                else:
                    # Handle pits without state information
                    states["Unknown"] = states.get("Unknown", 0) + 1

            print("   Distribution by state:")
            for state in sorted(states.keys()):
                print(f"     {state}: {states[state]} pits")

            print("\n✅ Download completed successfully!")
            print(
                f"\n💾 All data has been saved to the 'demos/data/snowpits/' directory"  # noqa: F541
            )
            print("🔄 Progress tracking allows resuming interrupted downloads")
        else:
            print("\n⚠️  No pits were downloaded (empty result)")
    else:
        print("\n⏸️  Download cancelled by user")
else:
    print("\n⚠️  No pits found for the specified query parameters")

print("\n✅ Test completed successfully!")
