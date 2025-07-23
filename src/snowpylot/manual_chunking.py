"""
Manual Chunking Utilities for SnowPilot Query Engine

This module provides utilities for manually chunking queries to work around
the snowpilot.org API caching bug that causes sequential requests to return
the same cached results.
"""

import time
import logging
from datetime import datetime, timedelta
from typing import List, Tuple, Optional
from dataclasses import dataclass

from .query_engine import QueryEngine, QueryFilter, QueryResult

logger = logging.getLogger(__name__)


@dataclass
class ChunkResult:
    """Result from processing a single chunk"""

    chunk_id: str
    start_date: str
    end_date: str
    success: bool
    pit_count: int = 0
    error_message: Optional[str] = None


@dataclass
class ManualChunkingResult:
    """Result from manual chunking process"""

    total_chunks: int
    successful_chunks: int
    failed_chunks: int
    total_pits: int
    chunk_results: List[ChunkResult]
    all_pits: List = None  # Will contain SnowPit objects


def generate_date_chunks(
    start_date: str, end_date: str, chunk_size_days: int
) -> List[Tuple[str, str]]:
    """
    Generate date chunks for manual processing

    Args:
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format
        chunk_size_days: Size of each chunk in days

    Returns:
        List of (start_date, end_date) tuples for each chunk
    """
    chunks = []
    current_date = datetime.strptime(start_date, "%Y-%m-%d")
    end_date_obj = datetime.strptime(end_date, "%Y-%m-%d")

    while current_date <= end_date_obj:
        chunk_end = current_date + timedelta(days=chunk_size_days - 1)
        if chunk_end > end_date_obj:
            chunk_end = end_date_obj

        chunks.append(
            (current_date.strftime("%Y-%m-%d"), chunk_end.strftime("%Y-%m-%d"))
        )
        current_date = chunk_end + timedelta(days=1)

    return chunks


def download_chunks_with_delay(
    engine: QueryEngine,
    chunks: List[Tuple[str, str]],
    base_query_filter: QueryFilter,
    delay_between_chunks: int = 60,
    auto_approve: bool = True,
    verbose: bool = True,
) -> ManualChunkingResult:
    """
    Download chunks with controlled delays to work around API caching bug

    Args:
        engine: QueryEngine instance
        chunks: List of (start_date, end_date) tuples
        base_query_filter: Base QueryFilter with common parameters (state, username, etc.)
        delay_between_chunks: Seconds to wait between chunks (default: 60)
        auto_approve: Whether to auto-approve downloads
        verbose: Whether to print progress messages

    Returns:
        ManualChunkingResult with summary and all downloaded pits
    """
    if verbose:
        print(
            f"Starting manual chunked download with {delay_between_chunks}s delays..."
        )

    all_pits = []
    chunk_results = []
    successful_chunks = 0
    failed_chunks = 0

    for i, (chunk_start, chunk_end) in enumerate(chunks):
        chunk_id = f"{chunk_start}_{chunk_end}"

        if verbose:
            print(
                f"\n🔄 Processing chunk {i + 1}/{len(chunks)}: {chunk_start} to {chunk_end}"
            )

        # Add delay before each chunk (except the first one) to work around API caching
        if i > 0:
            if verbose:
                print(
                    f"   ⏱️  Waiting {delay_between_chunks} seconds to avoid API caching..."
                )
            time.sleep(delay_between_chunks)

        # Create query filter for this chunk by copying base filter and updating dates
        chunk_filter = QueryFilter(
            pit_name=base_query_filter.pit_name,
            date_start=chunk_start,
            date_end=chunk_end,
            state=base_query_filter.state,
            states=base_query_filter.states,
            username=base_query_filter.username,
            organization_name=base_query_filter.organization_name,
            per_page=base_query_filter.per_page,
            max_retries=base_query_filter.max_retries,
        )

        try:
            # Download this chunk
            result = engine.download_results(chunk_filter, auto_approve=auto_approve)

            if result.status == "success":
                all_pits.extend(result.snow_pits)
                successful_chunks += 1
                chunk_result = ChunkResult(
                    chunk_id=chunk_id,
                    start_date=chunk_start,
                    end_date=chunk_end,
                    success=True,
                    pit_count=len(result.snow_pits),
                )
                if verbose:
                    print(f"   ✅ Success: Downloaded {len(result.snow_pits)} pits")

            elif result.status == "no_data":
                successful_chunks += 1
                chunk_result = ChunkResult(
                    chunk_id=chunk_id,
                    start_date=chunk_start,
                    end_date=chunk_end,
                    success=True,
                    pit_count=0,
                )
                if verbose:
                    print(f"   ℹ️  No data available for this date range")

            else:
                failed_chunks += 1
                error_msg = result.error_message or "Unknown error"
                chunk_result = ChunkResult(
                    chunk_id=chunk_id,
                    start_date=chunk_start,
                    end_date=chunk_end,
                    success=False,
                    error_message=error_msg,
                )
                if verbose:
                    print(f"   ❌ Failed: {error_msg}")

        except Exception as e:
            failed_chunks += 1
            error_msg = str(e)
            chunk_result = ChunkResult(
                chunk_id=chunk_id,
                start_date=chunk_start,
                end_date=chunk_end,
                success=False,
                error_message=error_msg,
            )
            if verbose:
                print(f"   ❌ Exception: {error_msg}")

        chunk_results.append(chunk_result)

    return ManualChunkingResult(
        total_chunks=len(chunks),
        successful_chunks=successful_chunks,
        failed_chunks=failed_chunks,
        total_pits=len(all_pits),
        chunk_results=chunk_results,
        all_pits=all_pits,
    )


def print_chunking_summary(
    result: ManualChunkingResult,
    start_date: str,
    end_date: str,
    chunk_size_days: int,
    delay_between_chunks: int,
):
    """Print a formatted summary of chunking results"""
    print(f"\n{'=' * 60}")
    print("📊 MANUAL CHUNKING SUMMARY")
    print(f"{'=' * 60}")
    print(f"✅ Successful chunks: {result.successful_chunks}/{result.total_chunks}")
    print(f"❌ Failed chunks: {result.failed_chunks}")
    print(f"📊 Total pits downloaded: {result.total_pits}")
    print(f"⏱️  Date range: {start_date} to {end_date}")
    print(f"🔧 Chunk size: {chunk_size_days} day(s)")
    print(f"⏰ Delay between chunks: {delay_between_chunks}s")

    if result.failed_chunks > 0:
        print(f"\n❌ Failed chunks ({result.failed_chunks}):")
        for chunk_result in result.chunk_results:
            if not chunk_result.success:
                print(f"  - {chunk_result.chunk_id}: {chunk_result.error_message}")
        print(f"\n💡 You can re-run failed chunks individually with longer delays")


def download_date_range_with_chunking(
    engine: QueryEngine,
    start_date: str,
    end_date: str,
    chunk_size_days: int = 1,
    delay_between_chunks: int = 60,
    state: Optional[str] = None,
    states: Optional[List[str]] = None,
    username: Optional[str] = None,
    organization_name: Optional[str] = None,
    auto_approve: bool = True,
    verbose: bool = True,
) -> ManualChunkingResult:
    """
    Convenience function to download a date range using manual chunking

    Args:
        engine: QueryEngine instance
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format
        chunk_size_days: Size of each chunk in days (default: 1)
        delay_between_chunks: Seconds to wait between chunks (default: 60)
        state: Single state code to filter by
        states: List of state codes for multi-state queries
        username: Username filter
        organization_name: Organization filter
        auto_approve: Whether to auto-approve downloads
        verbose: Whether to print progress messages

    Returns:
        ManualChunkingResult with summary and all downloaded pits
    """
    # Generate chunks
    chunks = generate_date_chunks(start_date, end_date, chunk_size_days)

    if verbose:
        print(f"Generated {len(chunks)} chunks:")
        for i, (chunk_start, chunk_end) in enumerate(chunks):
            print(f"  Chunk {i + 1}: {chunk_start} to {chunk_end}")

    # Create base query filter
    base_filter = QueryFilter(
        state=state,
        states=states,
        username=username,
        organization_name=organization_name,
        max_retries=3,  # More retries for individual chunks
    )

    # Download with chunking
    result = download_chunks_with_delay(
        engine=engine,
        chunks=chunks,
        base_query_filter=base_filter,
        delay_between_chunks=delay_between_chunks,
        auto_approve=auto_approve,
        verbose=verbose,
    )

    # Print summary
    if verbose:
        print_chunking_summary(
            result, start_date, end_date, chunk_size_days, delay_between_chunks
        )

    return result


# Example usage:
"""
from snowpylot.query_engine import QueryEngine
from snowpylot.manual_chunking import download_date_range_with_chunking

# Initialize engine
engine = QueryEngine(pits_path="data/snowpits")

# Download with manual chunking
result = download_date_range_with_chunking(
    engine=engine,
    start_date="2023-01-01",
    end_date="2023-01-31", 
    chunk_size_days=1,
    delay_between_chunks=60,
    state="MT",  # Optional state filter
    auto_approve=True
)

# Access results
print(f"Downloaded {result.total_pits} pits from {result.successful_chunks} chunks")
all_pits = result.all_pits  # List of SnowPit objects
"""
