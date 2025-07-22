"""
SnowPylot - A Python library for working with CAAML snow profile data
"""

__version__ = "1.1.3"

from .caaml_parser import caaml_parser
from .snow_pit import SnowPit
from .query_engine import QueryEngine, QueryFilter, QueryResult
from .manual_chunking import (
    download_date_range_with_chunking,
    download_chunks_with_delay,
    generate_date_chunks,
    print_chunking_summary,
    ChunkResult,
    ManualChunkingResult,
)

__all__ = [
    "SnowPit",
    "caaml_parser",
    "QueryEngine",
    "QueryFilter",
    "QueryResult",
    "download_date_range_with_chunking",
    "download_chunks_with_delay",
    "generate_date_chunks",
    "print_chunking_summary",
    "ChunkResult",
    "ManualChunkingResult",
]
