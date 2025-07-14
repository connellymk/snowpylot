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

print("\n=== Testing Large Dataset Download ===")

# Set up 5-year date range with 1-week chunking
start_date = "2019-09-01"  # September 1, 2019
end_date = "2024-08-31"  # August 31, 2024

print("Testing large dataset download:")
print(f"  Date range: {start_date} to {end_date}")
print("  Chunk size: 7 days (1 week)")
print("  State: MT (Montana)")
print("  This will download approximately 5 years of data")

# Create query filter with 1-week chunking
query_filter = QueryFilter(
    date_start=start_date,
    date_end=end_date,
    state="MT",
    per_page=100,
    auto_chunk=True,  # Enable automatic chunking
    chunk_size_days=7,  # 1 week chunks
    max_retries=3,  # Retry failed chunks up to 3 times
)

try:
    # Preview the query first
    print("\n--- Query Preview ---")
    preview = engine.preview_query(query_filter)
    print("✅ Preview completed!")
    print(f"   Estimated pits: {preview.estimated_count}")
    print(f"   Will be chunked: {preview.will_be_chunked}")
    print(f"   Estimated chunks: {preview.estimated_chunks}")
    print(f"   Chunk size: {query_filter.chunk_size_days} days")

    # Ask for confirmation given the large size
    if preview.estimated_count > 100:
        print(
            f"\n⚠️  WARNING: This will download {preview.estimated_count} pits using {preview.estimated_chunks} chunks"
        )
        print("   This may take significant time and bandwidth.")

        response = (
            input("\nDo you want to proceed with the download? (y/N): ").lower().strip()
        )
        if response not in ["y", "yes"]:
            print("❌ Download cancelled by user")
            sys.exit(0)

    # Execute the chunked query
    print("\n--- Starting Chunked Download ---")
    print("📊 Progress will be saved to 'data/snowpits/download_progress.json'")
    print(
        "💡 If interrupted, you can re-run this script to resume from where it left off"
    )

    result = engine.query_pits(query_filter, auto_approve=True)

    print("\n✅ Large dataset download completed!")
    print(f"   Total pits downloaded: {result.total_count}")
    print(f"   Was chunked: {result.was_chunked}")

    if result.was_chunked:
        print(f"   Total chunks: {result.download_info.get('total_chunks', 'N/A')}")
        print(
            f"   Completed chunks: {result.download_info.get('completed_chunks', 'N/A')}"
        )
        print(f"   Failed chunks: {result.download_info.get('failed_chunks', 'N/A')}")

    if result.download_info:
        saved_files = result.download_info.get("saved_files", [])
        if saved_files:
            print(f"   Files saved: {len(saved_files)}")
            print("   Example files:")
            for file in saved_files[:3]:  # Show first 3 files
                print(f"     - {file}")

    # Show some example pits if available
    if result.snow_pits:
        print("\n--- Example Pits ---")
        for i, pit in enumerate(result.snow_pits[:5]):  # Show first 5
            print(f"   Pit {i + 1}: {pit.core_info.pit_id} - {pit.core_info.pit_name}")
            if pit.core_info.location:
                print(f"     Location: {pit.core_info.location.region}")
            if pit.core_info.user:
                print(f"     User: {pit.core_info.user.username}")
            if pit.core_info.date:
                print(f"     Date: {pit.core_info.date}")

    # Show summary statistics
    if result.snow_pits:
        print("\n--- Dataset Summary ---")
        print(f"   Total pits: {len(result.snow_pits)}")

        # Group by year
        years = {}
        for pit in result.snow_pits:
            if pit.core_info.date:
                year = pit.core_info.date.year
                years[year] = years.get(year, 0) + 1

        print("   Distribution by year:")
        for year in sorted(years.keys()):
            print(f"     {year}: {years[year]} pits")

    print("\n✅ Test completed successfully!")
    print("\n💾 All data has been saved to the 'data/snowpits/' directory")
    print("🔄 Progress tracking allows resuming interrupted downloads")

except Exception as e:
    print(f"❌ Error during testing: {e}")
    print(f"   Error type: {type(e).__name__}")
    import traceback

    traceback.print_exc()
    print(
        "\n💡 If this was interrupted, you can re-run the script to resume from the last successful chunk"  # noqa: E501
    )
