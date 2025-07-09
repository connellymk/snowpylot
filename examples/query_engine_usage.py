#!/usr/bin/env python3
"""
Example usage of the SnowPylot Query Engine

This script demonstrates how to use the query engine to download and filter
snow pit data from snowpilot.org using various parameters.

Requirements:
    - Set SNOWPILOT_USER and SNOWPILOT_PASSWORD environment variables
    - Install required dependencies: requests, pandas
"""

import os
import sys
from datetime import datetime, timedelta

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from snowpylot.query_engine import (
    QueryEngine,
    QueryFilter,
    QueryResult,
    QueryPreview,
    query_by_date_range,
    query_by_pit_id,
    query_by_organization,
    query_by_location,
    preview_by_date_range,
)


def main():
    """Main function demonstrating various query patterns"""

    # Check environment variables
    if not os.environ.get("SNOWPILOT_USER") or not os.environ.get("SNOWPILOT_PASSWORD"):
        print(
            "Error: Please set SNOWPILOT_USER and SNOWPILOT_PASSWORD environment variables"
        )
        print("Example:")
        print("export SNOWPILOT_USER='your_username'")
        print("export SNOWPILOT_PASSWORD='your_password'")
        return

    # Initialize the query engine
    engine = QueryEngine(pits_path="data/downloaded_pits")

    print("=== SnowPylot Query Engine Examples ===\n")

    # Example 1: Preview query first, then download
    print("1. Preview query first, then download:")
    print("   Previewing pits from Montana for the last 30 days...")

    end_date = datetime.now().strftime("%Y-%m-%d")
    start_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")

    query_filter = QueryFilter(date_start=start_date, date_end=end_date, state="MT")

    # First, preview the query
    preview = engine.preview_query(query_filter, data_format="caaml")
    print(f"   Preview: {preview.estimated_count} pits would be downloaded")
    print(
        f"   Date range: {preview.query_filter.date_start} to {preview.query_filter.date_end}"
    )
    print(f"   State: {preview.query_filter.state}")

    # Now download with approval (will auto-approve if < 100 pits)
    result = engine.query_pits(query_filter, data_format="caaml")
    print(f"   Actually downloaded: {result.total_count} pits")
    print(f"   Downloaded to: {result.download_info.get('saved_file', 'N/A')}")
    print()

    # Example 2: Query by organization
    print("2. Query by organization:")
    print("   Searching for pits from 'Montana Avalanche Center'...")

    query_filter = QueryFilter(
        organization_name="Montana Avalanche Center",
        date_start=start_date,
        date_end=end_date,
    )

    result = engine.query_pits(query_filter)
    print(f"   Found {result.total_count} pits")
    print()

    # Example 3: Query by elevation range
    print("3. Query by elevation range:")
    print("   Searching for pits between 2000m and 3000m elevation...")

    query_filter = QueryFilter(
        elevation_min=2000,
        elevation_max=3000,
        date_start=start_date,
        date_end=end_date,
        state="MT",
    )

    result = engine.query_pits(query_filter)
    print(f"   Found {result.total_count} pits")
    print()

    # Example 4: Query by specific pit ID
    print("4. Query by specific pit ID:")
    print("   Searching for pit ID '13720'...")

    query_filter = QueryFilter(pit_id="13720")
    result = engine.query_pits(query_filter)

    if result.total_count > 0:
        pit = result.snow_pits[0]
        print(f"   Found pit: {pit.core_info.pit_name}")
        print(f"   Date: {pit.core_info.date}")
        print(
            f"   Location: {pit.core_info.location.country}, {pit.core_info.location.region}"
        )
        print(f"   User: {pit.core_info.user.username}")
        print(f"   Organization: {pit.core_info.user.operation_name}")
    else:
        print("   Pit not found")
    print()

    # Example 5: Query by username
    print("5. Query by username:")
    print("   Searching for pits by user 'benschmidt5'...")

    query_filter = QueryFilter(
        username="benschmidt5", date_start="2019-01-01", date_end="2019-12-31"
    )

    result = engine.query_pits(query_filter)
    print(f"   Found {result.total_count} pits")
    print()

    # Example 6: Query by aspect
    print("6. Query by aspect:")
    print("   Searching for north-facing pits...")

    query_filter = QueryFilter(
        aspect="N", date_start=start_date, date_end=end_date, state="MT"
    )

    result = engine.query_pits(query_filter)
    print(f"   Found {result.total_count} pits")
    print()

    # Example 7: Complex query with multiple filters
    print("7. Complex query with multiple filters:")
    print("   Searching for pits from professional operations,")
    print("   elevation > 2500m, north-facing slopes, last 30 days...")

    query_filter = QueryFilter(
        elevation_min=2500,
        aspect="N",
        date_start=start_date,
        date_end=end_date,
        state="MT",
    )

    result = engine.query_pits(query_filter)
    print(f"   Found {result.total_count} pits")

    if result.total_count > 0:
        print("   Sample pit details:")
        for i, pit in enumerate(result.snow_pits[:3]):  # Show first 3 pits
            print(f"     Pit {i + 1}: {pit.core_info.pit_name or 'Unnamed'}")
            print(f"       Date: {pit.core_info.date}")
            print(f"       Elevation: {pit.core_info.location.elevation}")
            print(f"       User: {pit.core_info.user.username}")
            print()

    # Example 8: Search local files
    print("8. Search local files:")
    print("   Searching locally saved pit files...")

    query_filter = QueryFilter(state="MT", elevation_min=2000)

    result = engine.search_local_pits(query_filter)
    print(f"   Found {result.total_count} local pits")
    print(f"   Searched {result.download_info.get('files_searched', 0)} files")
    print()

    # Example 9: Demonstrating large download with approval
    print("9. Demonstrating large download with approval:")
    print("   Querying for a large date range (this will request user approval)...")

    # Create a query that will likely have many results
    large_query_filter = QueryFilter(
        date_start="2019-01-01", date_end="2019-12-31", state="MT"
    )

    # Preview first to see the count
    preview = engine.preview_query(large_query_filter)
    print(f"   Preview shows {preview.estimated_count} pits would be downloaded")

    # This will request user approval if > 100 pits
    result = engine.query_pits(
        large_query_filter, auto_approve=False, approval_threshold=50
    )

    if result.download_info.get("status") == "cancelled":
        print("   Download was cancelled by user")
    else:
        print(f"   Downloaded {result.total_count} pits")
    print()

    # Example 10: Using convenience functions with auto-approval
    print("10. Using convenience functions with auto-approval:")
    print("   Using query_by_date_range function...")

    result = query_by_date_range(start_date, end_date, state="CO", auto_approve=True)
    print(f"   Found {result.total_count} pits from Colorado")
    print()

    print("   Using preview_by_date_range function...")
    preview = preview_by_date_range(start_date, end_date, state="MT")
    print(f"   Preview shows {preview.estimated_count} pits available")
    print()

    print("   Using query_by_location function with auto-approval...")
    result = query_by_location(
        country="US", state="MT", elevation_min=2000, auto_approve=True
    )
    print(f"   Found {result.total_count} pits from Montana above 2000m")
    print()

    print("=== Query Engine Examples Complete ===")


def demonstrate_data_structure():
    """Demonstrate the structure of returned data"""
    print("\n=== Data Structure Examples ===")

    # Search for a specific pit to demonstrate data structure
    engine = QueryEngine()

    # Try to find any pit from local files first
    query_filter = QueryFilter(pit_id="13720")
    result = engine.search_local_pits(query_filter)

    if result.total_count > 0:
        pit = result.snow_pits[0]
        print("Sample SnowPit object structure:")
        print(f"  Core Info:")
        print(f"    Pit ID: {pit.core_info.pit_id}")
        print(f"    Pit Name: {pit.core_info.pit_name}")
        print(f"    Date: {pit.core_info.date}")
        print(f"    Comment: {pit.core_info.comment}")
        print(f"  User Info:")
        print(f"    Username: {pit.core_info.user.username}")
        print(f"    Operation: {pit.core_info.user.operation_name}")
        print(f"    Professional: {pit.core_info.user.professional}")
        print(f"  Location:")
        print(f"    Country: {pit.core_info.location.country}")
        print(f"    Region: {pit.core_info.location.region}")
        print(f"    Elevation: {pit.core_info.location.elevation}")
        print(f"    Aspect: {pit.core_info.location.aspect}")
        print(f"    Slope Angle: {pit.core_info.location.slope_angle}")
        print(f"  Snow Profile:")
        print(f"    Profile Depth: {pit.snow_profile.profile_depth}")
        print(f"    Number of Layers: {len(pit.snow_profile.layers)}")
        print(f"    Temperature Observations: {len(pit.snow_profile.temp_profile)}")
        print(f"  Stability Tests:")
        print(f"    Compression Tests: {len(pit.stability_tests.compression_tests)}")
        print(
            f"    Extended Column Tests: {len(pit.stability_tests.extended_column_tests)}"
        )
        print(f"  Whumpf Data: {pit.whumpf_data is not None}")
    else:
        print("No local pit data found for demonstration")


if __name__ == "__main__":
    main()
    demonstrate_data_structure()
