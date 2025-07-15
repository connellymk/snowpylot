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

# Test both standard and chunked queries
print("1. Testing standard (non-chunked) query:")
standard_filter = QueryFilter(
    date_start="2023-01-01",
    date_end="2023-01-07",  # 1 week
    state="MT",
    chunk=False,  # Disable chunking
)

print("   Performing dry run for standard query...")
standard_dry_run = engine.dry_run(standard_filter)
print(f"\n{standard_dry_run}")

print("\n2. Testing chunked query:")
chunked_filter = QueryFilter(
    date_start="2023-01-01",
    date_end="2023-01-31",  # 1 month
    chunk=True,  # Enable chunking
    chunk_size_days=7,
)

print("   Performing dry run for chunked query...")
chunked_dry_run = engine.dry_run(chunked_filter)
print(f"\n{chunked_dry_run}")

print("\n=== Testing Pit Count Estimation ===")

# Test the new estimate_pit_count method directly
print("Testing direct pit count estimation (this downloads data to count files)...")
query_string = engine.query_builder.build_caaml_query(standard_filter)
estimated_count = engine.session.estimate_pit_count(query_string)
print(f"Direct estimation result: {estimated_count} pits")

print("\n=== Testing Large Dataset Download ===")

# Choose which query to use for the actual download
print("Choose which query to use for actual download:")
print("1. Standard query (1 week, no chunking)")
print("2. Chunked query (1 month, with chunking)")
print("3. Multi-state query (3 states, with chunking)")
print("4. Skip download")

choice = input("Enter your choice (1/2/3/4): ").strip()

if choice == "1":
    selected_filter = standard_filter
    selected_dry_run = standard_dry_run
    query_type = "standard"
elif choice == "2":
    selected_filter = chunked_filter
    selected_dry_run = chunked_dry_run
    query_type = "chunked"
elif choice == "3":
    # Multi-state query example
    multi_state_filter = QueryFilter(
        date_start="2023-01-01",
        date_end="2023-01-31",
        states=["MT", "CO", "WY"],
        chunk=True,
        chunk_size_days=7,
    )

    print("   Creating multi-state query for MT, CO, WY...")
    print("   Note: This will estimate pit counts for all states combined...")

    selected_filter = multi_state_filter
    selected_dry_run = None  # Multi-state dry run is handled differently
    query_type = "multi-state"
elif choice == "4":
    print("\n⏸️  Download skipped by user")
    selected_filter = None
else:
    print("\n❌ Invalid choice, skipping download")
    selected_filter = None

if selected_filter:
    if query_type == "multi-state":
        print(f"\n--- Multi-State Download ---")
        print(f"Query type: {query_type}")
        print(f"States: {', '.join(selected_filter.states)}")
        print(f"Date range: {selected_filter.date_start} to {selected_filter.date_end}")
        print(f"Will use chunking: {selected_filter.chunk_size_days} day chunks")

        proceed = (
            input(f"\nDo you want to proceed with multi-state download? (y/N): ")
            .lower()
            .strip()
        )
    else:
        print(f"\n--- {query_type.title()} Download Summary ---")
        print(f"Query type: {query_type}")
        print(f"Estimated pits: {selected_dry_run.total_estimated_pits}")
        if selected_dry_run.will_be_chunked:
            print(f"Will use chunking: {len(selected_dry_run.chunk_details)} chunks")

        proceed = (
            input(
                f"\nDo you want to proceed with downloading {selected_dry_run.total_estimated_pits} pits? (y/N): "
            )
            .lower()
            .strip()
        )

    if proceed in ["y", "yes"]:
        print("Starting download...")

        # Use the unified download_results method for all types
        result = engine.download_results(selected_filter, auto_approve=True)

        # Show detailed summary statistics
        if result.snow_pits:
            print("\n--- Dataset Summary ---")
            print(f"   Total pits downloaded: {len(result.snow_pits)}")
            print(f"   Was chunked: {result.was_chunked}")

            # Show multi-state info if applicable
            if result.download_info.get("multi_state", False):
                print(
                    f"   Multi-state download: {result.download_info.get('successful_states', 0)}/{result.download_info.get('total_states', 0)} states successful"
                )
                if result.download_info.get("states_processed"):
                    print(
                        f"   Successful states: {', '.join(result.download_info['states_processed'])}"
                    )
                if result.download_info.get("states_failed"):
                    print(
                        f"   Failed states: {', '.join(result.download_info['states_failed'])}"
                    )

            if result.was_chunked and result.chunk_results:
                print(f"   Chunks processed: {len(result.chunk_results)}")
                successful_chunks = sum(
                    1 for chunk in result.chunk_results if chunk.get("success", False)
                )
                print(f"   Successful chunks: {successful_chunks}")

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

            print("\n✅ Download completed successfully!")
            print(f"\n💾 All data has been saved to the '{download_path}' directory")
            if result.was_chunked:
                print("🔄 Progress tracking allows resuming interrupted downloads")
            if result.download_info.get("multi_state", False):
                print("🌐 Multi-state data has been combined into a single result")
        else:
            print("\n⚠️  No pits were downloaded (empty result)")
    else:
        print("\n⏸️  Download cancelled by user")
elif selected_filter:
    print(f"\n⚠️  No pits found for the specified query parameters")

print("\n✅ Test completed successfully!")
print("\n--- Summary of Changes ---")
print("📋 This updated test showcases the refactored query engine with:")
print("   • Unified download_results method for all dataset sizes")
print("   • Multi-state query support with automatic state handling")
print("   • Enhanced dry_run functionality with detailed chunk information")
print("   • Consolidated authentication and session management")
print("   • Improved pit count estimation method")
print("   • Better separation between standard and chunked queries")
print("   • More comprehensive result reporting")
