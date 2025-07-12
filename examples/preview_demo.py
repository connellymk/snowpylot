#!/usr/bin/env python3
"""
Simple demo of the new preview functionality in SnowPylot Query Engine

This script demonstrates how to preview queries before downloading.
"""

import os
import sys
from datetime import datetime, timedelta

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from snowpylot.query_engine import (
    QueryEngine,
    QueryFilter,
    QueryPreview,
    preview_by_date_range,
)


def main():
    """Demonstrate the preview functionality"""

    print("=== SnowPylot Query Engine Preview Demo ===\n")

    # Check environment variables
    if not os.environ.get("SNOWPILOT_USER") or not os.environ.get("SNOWPILOT_PASSWORD"):
        print(
            "Error: Please set SNOWPILOT_USER and SNOWPILOT_PASSWORD environment variables"
        )
        return

    # Initialize the query engine
    engine = QueryEngine()

    # Example 1: Preview a simple date range query
    print("1. Previewing a simple date range query:")
    end_date = datetime.now().strftime("%Y-%m-%d")
    start_date = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")

    query_filter = QueryFilter(date_start=start_date, date_end=end_date, state="MT")

    preview = engine.preview_query(query_filter)
    print(f"   {preview}")
    print()

    # Example 2: Preview a larger query
    print("2. Previewing a larger query (30 days):")
    start_date_30 = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")

    query_filter_30 = QueryFilter(
        date_start=start_date_30, date_end=end_date, state="MT"
    )

    preview_30 = engine.preview_query(query_filter_30)
    print(f"   {preview_30}")
    print()

    # Example 3: Preview with additional filters
    print("3. Previewing with elevation filter:")
    query_filter_elev = QueryFilter(
        date_start=start_date_30, date_end=end_date, state="MT", elevation_min=2000
    )

    preview_elev = engine.preview_query(query_filter_elev)
    print(f"   {preview_elev}")
    print()

    # Example 4: Using convenience function
    print("4. Using preview convenience function:")
    preview_conv = preview_by_date_range(start_date, end_date, state="CO")
    print(f"   {preview_conv}")
    print()

    # Example 5: Demonstrate the approval flow (without actually downloading)
    print("5. Demonstrating approval flow:")

    # Create a query that will likely have many results
    large_query = QueryFilter(
        date_start="2019-01-01", date_end="2019-12-31", state="MT"
    )

    preview_large = engine.preview_query(large_query)
    print(f"   {preview_large}")

    if preview_large.estimated_count > 100:
        print("   ⚠️  This query would trigger the approval prompt")
        print("   You would see a message like:")
        print(
            "   'This query will download approximately {} pits.'".format(
                preview_large.estimated_count
            )
        )
        print("   'Do you want to proceed with the download? (y/N):'")
    else:
        print("   ✅ This query would proceed automatically (< 100 pits)")
    print()

    print("=== Preview Demo Complete ===")


if __name__ == "__main__":
    main()
