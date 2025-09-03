#!/usr/bin/env python3
"""
Massive Snowpit Download Script
Download all snowpits from October 1, 2002 to July 31, 2024

This script uses adaptive chunking to efficiently download ~22 years of snowpit data,
accounting for seasonal variations in snowpit frequency.
"""

import os
import sys
import json
import time
from datetime import datetime, timedelta
from typing import List, Tuple, Dict
import logging

# Add src to path for imports
sys.path.append("src")

from snowpylot.query_engine import QueryEngine, QueryFilter

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("massive_download.log"), logging.StreamHandler()],
)
logger = logging.getLogger(__name__)


class AdaptiveChunkStrategy:
    """Adaptive chunking strategy based on seasonal snowpit patterns"""

    def __init__(self):
        # Define seasonal chunk sizes (in days)
        # Winter months typically have more snowpits, so use smaller chunks
        self.seasonal_chunk_sizes = {
            "winter_peak": 7,  # Dec-Feb: 7 days
            "winter": 14,  # Nov, Mar-Apr: 14 days
            "shoulder": 30,  # May, Oct: 30 days
            "summer": 60,  # Jun-Sep: 60 days
        }

    def get_season(self, date: datetime) -> str:
        """Determine season based on month"""
        month = date.month
        if month in [12, 1, 2]:
            return "winter_peak"
        elif month in [11, 3, 4]:
            return "winter"
        elif month in [5, 10]:
            return "shoulder"
        else:  # 6, 7, 8, 9
            return "summer"

    def generate_adaptive_chunks(
        self, start_date: str, end_date: str
    ) -> List[Tuple[str, str, str]]:
        """Generate chunks with adaptive sizing based on season

        Returns:
            List of (start_date, end_date, season) tuples
        """
        chunks = []
        current_date = datetime.strptime(start_date, "%Y-%m-%d")
        end_date_obj = datetime.strptime(end_date, "%Y-%m-%d")

        while current_date <= end_date_obj:
            season = self.get_season(current_date)
            chunk_size = self.seasonal_chunk_sizes[season]

            chunk_end = current_date + timedelta(days=chunk_size - 1)
            if chunk_end > end_date_obj:
                chunk_end = end_date_obj

            chunks.append(
                (
                    current_date.strftime("%Y-%m-%d"),
                    chunk_end.strftime("%Y-%m-%d"),
                    season,
                )
            )

            current_date = chunk_end + timedelta(days=1)

        return chunks


class ProgressTracker:
    """Track and save download progress"""

    def __init__(self, progress_file: str = "download_progress.json"):
        self.progress_file = progress_file
        self.progress = self.load_progress()

    def load_progress(self) -> Dict:
        """Load existing progress from file"""
        if os.path.exists(self.progress_file):
            try:
                with open(self.progress_file, "r") as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"Could not load progress file: {e}")

        return {
            "completed_chunks": [],
            "failed_chunks": [],
            "total_pits_downloaded": 0,
            "start_time": None,
            "last_update": None,
        }

    def save_progress(self):
        """Save current progress to file"""
        try:
            with open(self.progress_file, "w") as f:
                json.dump(self.progress, f, indent=2)
        except Exception as e:
            logger.error(f"Could not save progress: {e}")

    def mark_chunk_completed(self, chunk_id: str, pit_count: int):
        """Mark a chunk as completed"""
        if chunk_id not in self.progress["completed_chunks"]:
            self.progress["completed_chunks"].append(chunk_id)
            self.progress["total_pits_downloaded"] += pit_count
            self.progress["last_update"] = datetime.now().isoformat()
            self.save_progress()

    def mark_chunk_failed(self, chunk_id: str, error: str):
        """Mark a chunk as failed"""
        failed_entry = {
            "chunk_id": chunk_id,
            "error": error,
            "timestamp": datetime.now().isoformat(),
        }
        self.progress["failed_chunks"].append(failed_entry)
        self.save_progress()

    def is_chunk_completed(self, chunk_id: str) -> bool:
        """Check if a chunk has already been completed"""
        return chunk_id in self.progress["completed_chunks"]

    def get_stats(self) -> Dict:
        """Get current progress statistics"""
        return {
            "completed_chunks": len(self.progress["completed_chunks"]),
            "failed_chunks": len(self.progress["failed_chunks"]),
            "total_pits": self.progress["total_pits_downloaded"],
        }


def break_chunk_into_days(start_date: str, end_date: str) -> List[Tuple[str, str]]:
    """Break a chunk into individual day chunks"""
    days = []
    current_date = datetime.strptime(start_date, "%Y-%m-%d")
    end_date_obj = datetime.strptime(end_date, "%Y-%m-%d")

    while current_date <= end_date_obj:
        day_str = current_date.strftime("%Y-%m-%d")
        days.append((day_str, day_str))
        current_date += timedelta(days=1)

    return days


def estimate_download_time(total_chunks: int, delay_between_chunks: int = 60) -> str:
    """Estimate total download time"""
    total_seconds = total_chunks * (
        delay_between_chunks + 30
    )  # 30s per request estimate
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60

    if hours > 24:
        days = hours // 24
        hours = hours % 24
        return f"~{days} days, {hours} hours, {minutes} minutes"
    else:
        return f"~{hours} hours, {minutes} minutes"


def main():
    """Main download function"""
    print("=" * 80)
    print("🏔️  MASSIVE SNOWPIT DOWNLOAD - October 2015 to July 2024")
    print("=" * 80)

    # Configuration
    START_DATE = "2015-10-01"
    END_DATE = "2024-07-31"
    DELAY_BETWEEN_CHUNKS = 10  # seconds
    DOWNLOAD_PATH = "data/massive_snowpit_download"

    # Set up environment
    print("\n1️⃣  Setting up environment...")
    os.environ["SNOWPILOT_USER"] = "katisthebatis"
    os.environ["SNOWPILOT_PASSWORD"] = "mkconn123"

    # Initialize components
    print("\n2️⃣  Initializing download components...")
    engine = QueryEngine(pits_path=DOWNLOAD_PATH)
    chunker = AdaptiveChunkStrategy()
    tracker = ProgressTracker()

    # Test authentication
    print("\n3️⃣  Testing authentication...")
    if not engine.session.authenticate():
        print("❌ Authentication failed! Check your credentials.")
        sys.exit(1)
    print("✅ Authentication successful!")

    # Generate adaptive chunks
    print("\n4️⃣  Generating adaptive chunks...")
    chunks = chunker.generate_adaptive_chunks(START_DATE, END_DATE)

    # Filter out already completed chunks
    remaining_chunks = []
    for chunk_start, chunk_end, season in chunks:
        chunk_id = f"{chunk_start}_{chunk_end}"
        if not tracker.is_chunk_completed(chunk_id):
            remaining_chunks.append((chunk_start, chunk_end, season))

    print(f"📊 Total chunks generated: {len(chunks)}")
    print(f"✅ Already completed: {len(chunks) - len(remaining_chunks)}")
    print(f"⏳ Remaining chunks: {len(remaining_chunks)}")

    # Show chunk distribution by season
    season_counts = {}
    for _, _, season in chunks:
        season_counts[season] = season_counts.get(season, 0) + 1

    print(f"\n📈 Chunk distribution by season:")
    for season, count in season_counts.items():
        chunk_size = chunker.seasonal_chunk_sizes[season]
        print(f"   {season}: {count} chunks ({chunk_size} days each)")

    # Estimate download time
    estimated_time = estimate_download_time(len(remaining_chunks), DELAY_BETWEEN_CHUNKS)
    print(f"\n⏱️  Estimated download time: {estimated_time}")

    # Get user confirmation
    if remaining_chunks:
        response = (
            input(f"\n🚀 Ready to download {len(remaining_chunks)} chunks? (y/N): ")
            .lower()
            .strip()
        )
        if response not in ["y", "yes"]:
            print("Download cancelled.")
            sys.exit(0)
    else:
        print("🎉 All chunks already completed!")
        return

    # Start download
    print(f"\n🚀 Starting massive download...")
    print(f"   Date range: {START_DATE} to {END_DATE}")
    print(f"   Delay between chunks: {DELAY_BETWEEN_CHUNKS}s")
    print(f"   Download path: {DOWNLOAD_PATH}")

    tracker.progress["start_time"] = datetime.now().isoformat()
    tracker.save_progress()

    # Download chunks
    all_pits = []
    successful_chunks = 0
    failed_chunks = 0

    for i, (chunk_start, chunk_end, season) in enumerate(remaining_chunks):
        chunk_id = f"{chunk_start}_{chunk_end}"
        chunk_size = chunker.seasonal_chunk_sizes[season]

        print(f"\n🔄 Processing chunk {i + 1}/{len(remaining_chunks)}")
        print(f"   📅 Date range: {chunk_start} to {chunk_end}")
        print(f"   🌍 Season: {season} ({chunk_size} days)")

        # Add delay between chunks (except first)
        if i > 0:
            print(f"   ⏱️  Waiting {DELAY_BETWEEN_CHUNKS}s to avoid API caching...")
            time.sleep(DELAY_BETWEEN_CHUNKS)

        # Create query filter for this chunk (no retries - attempt once)
        chunk_filter = QueryFilter(
            date_start=chunk_start, date_end=chunk_end, max_retries=1
        )

        try:
            # Download this chunk
            result = engine.download_results(chunk_filter, auto_approve=True)

            if result.status == "success":
                pit_count = len(result.snow_pits)
                all_pits.extend(result.snow_pits)
                successful_chunks += 1
                tracker.mark_chunk_completed(chunk_id, pit_count)
                print(f"   ✅ Success: Downloaded {pit_count} pits")

            elif result.status == "no_data":
                successful_chunks += 1
                tracker.mark_chunk_completed(chunk_id, 0)
                print(f"   ℹ️  No data available for this date range")

            else:
                # Chunk failed - break down into 1-day chunks
                print(f"   ❌ Chunk failed: {result.error_message or 'Unknown error'}")
                print(f"   🔄 Breaking down into 1-day chunks...")

                day_chunks = break_chunk_into_days(chunk_start, chunk_end)
                chunk_pit_count = 0
                successful_days = 0
                failed_days = 0

                for day_start, day_end in day_chunks:
                    day_filter = QueryFilter(
                        date_start=day_start, date_end=day_end, max_retries=1
                    )

                    try:
                        day_result = engine.download_results(
                            day_filter, auto_approve=True
                        )

                        if day_result.status == "success":
                            day_pit_count = len(day_result.snow_pits)
                            all_pits.extend(day_result.snow_pits)
                            chunk_pit_count += day_pit_count
                            successful_days += 1
                            print(f"     ✅ {day_start}: {day_pit_count} pits")

                        elif day_result.status == "no_data":
                            successful_days += 1
                            print(f"     ℹ️  {day_start}: No data")

                        else:
                            failed_days += 1
                            error_msg = day_result.error_message or "Unknown error"
                            print(f"     ❌ {day_start}: Failed - {error_msg}")

                    except Exception as day_e:
                        failed_days += 1
                        print(f"     ❌ {day_start}: Exception - {str(day_e)}")

                    # Small delay between day requests
                    if day_start != day_chunks[-1][0]:  # Not the last day
                        time.sleep(2)

                # Mark chunk as completed with whatever data we got
                successful_chunks += 1
                tracker.mark_chunk_completed(chunk_id, chunk_pit_count)
                breakdown_msg = (
                    f"   📊 Chunk breakdown complete: {successful_days} successful days, "
                    f"{failed_days} failed days, {chunk_pit_count} total pits"
                )
                print(breakdown_msg)

        except Exception as e:
            # Unexpected exception - try breaking down into days as fallback
            print(f"   ❌ Unexpected exception: {str(e)}")
            print(f"   🔄 Attempting 1-day chunk breakdown as fallback...")

            try:
                day_chunks = break_chunk_into_days(chunk_start, chunk_end)
                chunk_pit_count = 0
                successful_days = 0
                failed_days = 0

                for day_start, day_end in day_chunks:
                    day_filter = QueryFilter(
                        date_start=day_start, date_end=day_end, max_retries=1
                    )

                    try:
                        day_result = engine.download_results(
                            day_filter, auto_approve=True
                        )

                        if day_result.status == "success":
                            day_pit_count = len(day_result.snow_pits)
                            all_pits.extend(day_result.snow_pits)
                            chunk_pit_count += day_pit_count
                            successful_days += 1
                            print(f"     ✅ {day_start}: {day_pit_count} pits")

                        elif day_result.status == "no_data":
                            successful_days += 1
                            print(f"     ℹ️  {day_start}: No data")

                        else:
                            failed_days += 1
                            print(f"     ❌ {day_start}: Failed")

                    except Exception:
                        failed_days += 1
                        print(f"     ❌ {day_start}: Exception")

                    # Small delay between day requests
                    if day_start != day_chunks[-1][0]:  # Not the last day
                        time.sleep(2)

                # Mark chunk as completed with whatever data we got
                successful_chunks += 1
                tracker.mark_chunk_completed(chunk_id, chunk_pit_count)
                fallback_msg = (
                    f"   📊 Fallback breakdown complete: {successful_days} successful days, "
                    f"{failed_days} failed days, {chunk_pit_count} total pits"
                )
                print(fallback_msg)

            except Exception as fallback_e:
                # Complete failure - mark as failed
                failed_chunks += 1
                error_msg = f"Complete failure: {str(fallback_e)}"
                tracker.mark_chunk_failed(chunk_id, error_msg)
                print(f"   ❌ Complete failure: {error_msg}")

        # Print progress summary every 10 chunks
        if (i + 1) % 10 == 0:
            stats = tracker.get_stats()
            print(f"\n📊 Progress Summary (after {i + 1} chunks):")
            print(f"   ✅ Completed: {stats['completed_chunks']}")
            print(f"   ❌ Failed: {stats['failed_chunks']}")
            print(f"   📊 Total pits: {stats['total_pits']}")

    # Final summary
    print(f"\n{'=' * 80}")
    print("🏁 MASSIVE DOWNLOAD COMPLETE!")
    print(f"{'=' * 80}")

    final_stats = tracker.get_stats()
    print(f"✅ Successful chunks: {successful_chunks}")
    print(f"❌ Failed chunks: {failed_chunks}")
    print(f"📊 Total pits downloaded: {final_stats['total_pits']}")
    print(f"📁 Download location: {DOWNLOAD_PATH}")

    if failed_chunks > 0:
        print(f"\n⚠️  There were {failed_chunks} failed chunks.")
        print(
            "💡 Check download_progress.json for details and re-run to retry failed chunks."
        )

    print("\n🎉 Download completed successfully!")


if __name__ == "__main__":
    main()
