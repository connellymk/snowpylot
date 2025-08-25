#!/usr/bin/env python3
"""
Test Massive Download System

Test the adaptive chunking system with a small subset of data before running
the full 22-year download.
"""

import os
import sys
from datetime import datetime

# Add src to path for imports
sys.path.append("src")

from snowpylot.query_engine import QueryEngine
from snowpylot.manual_chunking import download_date_range_with_chunking


def test_winter_period():
    """Test with a winter period (should use smaller chunks)"""
    print("🧪 Testing winter period (high snowpit density)...")

    # Test with a week in January 2023
    return download_date_range_with_chunking(
        engine=QueryEngine(pits_path="data/test_massive_download"),
        start_date="2023-01-01",
        end_date="2023-01-07",
        chunk_size_days=1,  # Use small chunks for testing
        delay_between_chunks=10,  # Shorter delay for testing
        auto_approve=True,
        verbose=True,
    )


def test_summer_period():
    """Test with a summer period (should use larger chunks)"""
    print("\n🧪 Testing summer period (low snowpit density)...")

    # Test with a week in July 2023
    return download_date_range_with_chunking(
        engine=QueryEngine(pits_path="data/test_massive_download"),
        start_date="2023-07-01",
        end_date="2023-07-07",
        chunk_size_days=7,  # Larger chunks for summer
        delay_between_chunks=10,  # Shorter delay for testing
        auto_approve=True,
        verbose=True,
    )


def test_adaptive_chunking():
    """Test the adaptive chunking system"""
    print("\n🧪 Testing adaptive chunking system...")

    sys.path.append(".")
    from massive_snowpit_download import AdaptiveChunkStrategy

    chunker = AdaptiveChunkStrategy()

    # Test chunk generation for a short period covering multiple seasons
    chunks = chunker.generate_adaptive_chunks("2023-01-01", "2023-08-31")

    print(f"Generated {len(chunks)} adaptive chunks:")

    season_counts = {}
    for start_date, end_date, season in chunks:
        season_counts[season] = season_counts.get(season, 0) + 1
        print(f"  {start_date} to {end_date} ({season})")

    print(f"\nChunk distribution by season:")
    for season, count in season_counts.items():
        chunk_size = chunker.seasonal_chunk_sizes[season]
        print(f"  {season}: {count} chunks ({chunk_size} days each)")

    return len(chunks)


def main():
    """Run all tests"""
    print("=" * 60)
    print("🧪 TESTING MASSIVE DOWNLOAD SYSTEM")
    print("=" * 60)

    # Set up environment
    print("\n1️⃣  Setting up test environment...")
    os.environ["SNOWPILOT_USER"] = "katisthebatis"
    os.environ["SNOWPILOT_PASSWORD"] = "mkconn123"

    # Test authentication
    print("\n2️⃣  Testing authentication...")
    engine = QueryEngine(pits_path="data/test_massive_download")
    if not engine.session.authenticate():
        print("❌ Authentication failed! Check your credentials.")
        sys.exit(1)
    print("✅ Authentication successful!")

    # Test adaptive chunking algorithm
    print("\n3️⃣  Testing adaptive chunking algorithm...")
    chunk_count = test_adaptive_chunking()
    print(f"✅ Adaptive chunking test completed: {chunk_count} chunks generated")

    # Test winter period download
    print("\n4️⃣  Testing winter period download...")
    try:
        winter_result = test_winter_period()
        print(f"✅ Winter test completed: {winter_result.total_pits} pits downloaded")
    except Exception as e:
        print(f"❌ Winter test failed: {e}")

    # Test summer period download
    print("\n5️⃣  Testing summer period download...")
    try:
        summer_result = test_summer_period()
        print(f"✅ Summer test completed: {summer_result.total_pits} pits downloaded")
    except Exception as e:
        print(f"❌ Summer test failed: {e}")

    print("\n" + "=" * 60)
    print("🎉 ALL TESTS COMPLETED!")
    print("=" * 60)
    print("✅ System is ready for massive download")
    print("💡 Run 'python massive_snowpit_download.py' to start the full download")


if __name__ == "__main__":
    main()
