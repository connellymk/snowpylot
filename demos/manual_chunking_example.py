#!/usr/bin/env python3
"""
Example: Manual Chunking with SnowPylot

This example demonstrates how to use the manual chunking utilities to work around
the snowpilot.org API caching bug that causes duplicate data across date ranges.
"""

import os
import sys

# Add src to path for imports
sys.path.append("../src")

from snowpylot import QueryEngine, download_date_range_with_chunking


def main():
    # Check environment variables
    user = os.environ.get("SNOWPILOT_USER")
    password = os.environ.get("SNOWPILOT_PASSWORD")

    if not user or not password:
        print(
            "❌ Error: SNOWPILOT_USER and SNOWPILOT_PASSWORD environment variables required"
        )
        sys.exit(1)

    print("🔧 SnowPylot Manual Chunking Example")
    print("=" * 50)

    # Initialize query engine
    engine = QueryEngine(pits_path="data/snowpits")

    # Test authentication
    if not engine.session.authenticate():
        print("❌ Authentication failed!")
        sys.exit(1)

    print("✅ Authentication successful")

    # Example 1: Simple date range with 1-day chunks
    print("\n📅 Example 1: January 1-5, 2023 (1-day chunks, 30s delays)")
    result1 = download_date_range_with_chunking(
        engine=engine,
        start_date="2023-01-01",
        end_date="2023-01-05",
        chunk_size_days=1,
        delay_between_chunks=30,  # Shorter delay for testing
        auto_approve=True,
    )

    # Example 2: State-filtered query with longer chunks
    print("\n🏔️ Example 2: Montana only, January 10-15, 2023 (2-day chunks, 60s delays)")
    result2 = download_date_range_with_chunking(
        engine=engine,
        start_date="2023-01-10",
        end_date="2023-01-15",
        chunk_size_days=2,
        delay_between_chunks=60,
        state="MT",  # Montana only
        auto_approve=True,
    )

    # Example 3: Multi-state query
    print("\n🌍 Example 3: Multiple states, January 20-22, 2023 (1-day chunks)")
    result3 = download_date_range_with_chunking(
        engine=engine,
        start_date="2023-01-20",
        end_date="2023-01-22",
        chunk_size_days=1,
        delay_between_chunks=45,
        states=["MT", "CO", "WY"],  # Multiple western states
        auto_approve=True,
    )

    # Overall summary
    total_pits = result1.total_pits + result2.total_pits + result3.total_pits
    total_chunks = result1.total_chunks + result2.total_chunks + result3.total_chunks
    successful_chunks = (
        result1.successful_chunks
        + result2.successful_chunks
        + result3.successful_chunks
    )

    print("\n" + "=" * 60)
    print("🎯 OVERALL SUMMARY")
    print("=" * 60)
    print(f"✅ Total successful chunks: {successful_chunks}/{total_chunks}")
    print(f"📊 Total pits downloaded: {total_pits}")
    print(f"📁 Data saved to: {os.path.abspath('data/snowpits')}")

    # Show sample data if available
    if total_pits > 0:
        sample_pit = (
            result1.all_pits[0]
            if result1.all_pits
            else (result2.all_pits[0] if result2.all_pits else result3.all_pits[0])
        )
        print(f"\n=== Sample Pit Data ===")
        print(f"Pit Name: {sample_pit.core_info.pit_name}")
        print(f"Location: {sample_pit.core_info.location}")
        print(f"Date: {sample_pit.core_info.date}")
        print(f"Observer: {sample_pit.core_info.observer}")
        print(f"Layers: {len(sample_pit.layers)}")

    print("\n✨ Manual chunking completed successfully!")
    print("💡 Tip: Increase delay_between_chunks if you still see duplicate data")


if __name__ == "__main__":
    main()
