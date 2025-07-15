"""
Query Engine for SnowPilot.org CAAML Data

This module provides tools for downloading and querying CAAML snow pit data
from snowpilot.org with flexible filtering capabilities, including automatic
handling of large datasets through chunking and progress tracking.

Supported API Filter Fields:
- pit_name: Filter by pit name
- state: Filter by state code (e.g., 'MT', 'CO', 'WY')
- date_start/date_end: Filter by date range (YYYY-MM-DD format)
- username: Filter by username
- organization_name: Filter by organization name
- per_page: Number of results per page (max 100)
"""

import json
import logging
import os
import re
import shutil
import tarfile
import tempfile
import time
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from glob import glob
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import requests

from .caaml_parser import caaml_parser
from .snow_pit import SnowPit

# Configuration constants
DEFAULT_PITS_PATH = "data/snowpits"
DEFAULT_REQUEST_DELAY = 5  # seconds between requests to prevent rate limiting
CHUNK_SIZE_DAYS = 7  # default chunk size in days for large datasets
RESULTS_PER_PAGE = 1000  # default number of results per page

# Create basic logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class QueryFilter:
    """
    Data class for query filter parameters

    Fields used in API calls (sent to snowpilot.org):
    - pit_name: Filter by pit name
    - state: Filter by state code (e.g., 'MT', 'CO', 'WY')
    - states: List of state codes for multi-state queries (e.g., ['MT', 'CO', 'WY'])
    - date_start/date_end: Filter by date range (YYYY-MM-DD format)
    - username: Filter by username
    - organization_name: Filter by organization name
    - per_page: Number of results per page (max 100)

    Configuration fields:
    - chunk: Enable chunking for large datasets (user-controlled)
    - chunk_size_days: Size of chunks in days (used when chunk=True)
    - max_retries: Maximum retry attempts for failed chunks
    """

    pit_name: Optional[str] = None
    date_start: Optional[Union[str, datetime, Any]] = (
        None  # Format: YYYY-MM-DD or datetime-like object
    )
    date_end: Optional[Union[str, datetime, Any]] = (
        None  # Format: YYYY-MM-DD or datetime-like object
    )
    state: Optional[str] = None
    states: Optional[List[str]] = None  # For multi-state queries
    username: Optional[str] = None
    organization_name: Optional[str] = None
    per_page: int = RESULTS_PER_PAGE  # Default per page limit
    chunk: bool = False  # User-controlled chunking
    chunk_size_days: int = CHUNK_SIZE_DAYS  # Size of chunks in days
    max_retries: int = 3  # Maximum retry attempts for failed chunks


@dataclass
class ChunkInfo:
    """Information about a single chunk"""

    chunk_id: str
    start_date: str
    end_date: str


@dataclass
class DryRunResult:
    """Data class for dry run information"""

    query_filter: Optional[QueryFilter] = None
    total_estimated_pits: int = 0
    will_be_chunked: bool = False
    chunk_size_days: int = 0
    chunk_details: List[ChunkInfo] = field(default_factory=list)

    def __str__(self) -> str:
        """Return a formatted dry run string"""
        if not self.will_be_chunked:
            return (
                f"Dry Run Result:\n"
                f"  Query Type: Single request\n"
                f"  Date range: {self.query_filter.date_start} to {self.query_filter.date_end}\n"
                f"  State: {self.query_filter.state or 'Any'}\n"
                f"  Username: {self.query_filter.username or 'Any'}\n"
                f"  Organization: {self.query_filter.organization_name or 'Any'}\n"
                f"  Estimated pits: {self.total_estimated_pits}\n"
                f"  Format: CAAML"
            )

        chunk_details = "\n".join(
            [
                f"    Chunk {i + 1}: {chunk.start_date} to {chunk.end_date}"
                for i, chunk in enumerate(self.chunk_details)
            ]
        )

        return (
            f"Dry Run Result:\n"
            f"  Query Type: Chunked ({len(self.chunk_details)} chunks)\n"
            f"  Chunk size: {self.chunk_size_days} days\n"
            f"  Date range: {self.query_filter.date_start} to {self.query_filter.date_end}\n"
            f"  State: {self.query_filter.state or 'Any'}\n"
            f"  Username: {self.query_filter.username or 'Any'}\n"
            f"  Organization: {self.query_filter.organization_name or 'Any'}\n"
            f"  Total estimated pits: {self.total_estimated_pits}\n"
            f"  Format: CAAML\n"
            f"  Chunk breakdown:\n{chunk_details}"
        )


@dataclass
class QueryResult:
    """Data class for query results"""

    snow_pits: List[SnowPit] = field(default_factory=list)
    total_count: int = 0
    query_filter: Optional[QueryFilter] = None
    download_info: Dict[str, Any] = field(default_factory=dict)
    dry_run_result: Optional[DryRunResult] = None
    chunk_results: List[Dict[str, Any]] = field(default_factory=list)
    was_chunked: bool = False
    status: str = "success"  # "success", "failed", "no_data"
    error_message: Optional[str] = None


@dataclass
class ProgressTracker:
    """Data class for tracking download progress"""

    completed_chunks: List[str] = field(default_factory=list)
    failed_chunks: List[str] = field(default_factory=list)
    total_pits: int = 0
    start_time: Optional[str] = None
    last_update: Optional[str] = None
    chunk_results: List[Dict[str, Any]] = field(default_factory=list)


class QueryBuilder:
    """Builds query parameters for snowpilot.org CAAML API"""

    def __init__(self):
        self.supported_states = {
            "MT": "Montana",
            "CO": "Colorado",
            "WY": "Wyoming",
            "UT": "Utah",
            "ID": "Idaho",
            "WA": "Washington",
            "OR": "Oregon",
            "CA": "California",
            "AK": "Alaska",
            "NH": "New Hampshire",
            "VT": "Vermont",
            "ME": "Maine",
            "NY": "New York",
        }

    def build_caaml_query(self, query_filter: QueryFilter) -> str:
        """Build query string for CAAML endpoint with all required form parameters"""
        params = []

        # Add all required form parameters (even if empty) to match the working URLs
        params.append(f"PIT_NAME={query_filter.pit_name or ''}")

        # STATE parameter
        if query_filter.state:
            if query_filter.state not in self.supported_states:
                raise ValueError(
                    f"State '{query_filter.state}' not supported. Supported states: {list(self.supported_states.keys())}"
                )
            params.append(f"STATE={query_filter.state}")
        else:
            params.append("STATE=")  # Empty but present

        # Date parameters
        params.append(f"OBS_DATE_MIN={query_filter.date_start or ''}")
        params.append(f"OBS_DATE_MAX={query_filter.date_end or ''}")

        # This seems to be required by the server
        params.append("recent_dates=0")

        # User and organization parameters
        params.append(f"USERNAME={query_filter.username or ''}")
        params.append(f"AFFIL={query_filter.organization_name or ''}")

        # Per page parameter (use 100 like the working implementation)
        per_page = min(query_filter.per_page, RESULTS_PER_PAGE)
        params.append(f"per_page={per_page}")

        # Advanced query parameter (always empty)
        params.append("ADV_WHERE_QUERY=")

        # Form submit parameter
        params.append("submit=Get+Pits")

        return "&".join(params)


class SnowPilotSession:
    """Manages authentication and session with snowpilot.org"""

    def __init__(self):
        self.session = requests.Session()
        self.authenticated = False
        self.site_url = "https://snowpilot.org"
        self.login_url = self.site_url + "/user/login"
        self.caaml_query_url = self.site_url + "/avscience-query-caaml.xml?"
        self.data_url = "https://snowpilot.org/sites/default/files/tmp/"
        self.last_request_time = 0
        self.request_delay = DEFAULT_REQUEST_DELAY

    def _enforce_rate_limit(self):
        """Enforce rate limiting between requests"""
        current_time = time.time()
        time_since_last_request = current_time - self.last_request_time

        if time_since_last_request < self.request_delay:
            sleep_time = self.request_delay - time_since_last_request
            logger.debug(f"Rate limiting: sleeping for {sleep_time:.2f} seconds")
            time.sleep(sleep_time)

        self.last_request_time = time.time()

    def authenticate(self) -> bool:
        """Authenticate with snowpilot.org"""
        user = os.environ.get("SNOWPILOT_USER")
        password = os.environ.get("SNOWPILOT_PASSWORD")

        if not user or not password:
            logger.error(
                "SNOWPILOT_USER and SNOWPILOT_PASSWORD environment variables required"
            )
            return False

        payload = {
            "name": user,
            "pass": password,
            "form_id": "user_login",
            "op": "Log in",
        }

        try:
            response = self.session.post(self.login_url, data=payload)
            self.authenticated = response.status_code == 200

            if self.authenticated:
                logger.info("Successfully authenticated with snowpilot.org")
            else:
                logger.error(
                    f"Authentication failed with status {response.status_code}"
                )

            return self.authenticated

        except requests.RequestException as e:
            logger.error(f"Authentication error: {e}")
            return False

    def _create_authenticated_session(self) -> Optional[requests.Session]:
        """Create an authenticated session for making requests"""
        user = os.environ.get("SNOWPILOT_USER")
        password = os.environ.get("SNOWPILOT_PASSWORD")

        if not user or not password:
            logger.error(
                "SNOWPILOT_USER and SNOWPILOT_PASSWORD environment variables required"
            )
            return None

        payload = {
            "name": user,
            "pass": password,
            "form_id": "user_login",
            "op": "Log in",
        }

        session = requests.Session()
        try:
            login_response = session.post(self.login_url, data=payload)
            if login_response.status_code == 200:
                return session
            else:
                logger.error(f"Login failed with status {login_response.status_code}")
                return None
        except requests.RequestException as e:
            logger.error(f"Authentication error: {e}")
            return None

    def _make_caaml_request(
        self, query_string: str, max_retries: int = 3
    ) -> tuple[Optional[bytes], Optional[str]]:
        """
        Make a CAAML request and return the data and filename

        Args:
            query_string: The query string to request
            max_retries: Maximum number of retry attempts

        Returns:
            Tuple of (data_bytes, filename) or (None, None) if failed
        """
        for attempt in range(max_retries):
            try:
                # Create authenticated session
                session = self._create_authenticated_session()
                if not session:
                    if attempt < max_retries - 1:
                        logger.info(
                            f"Retrying authentication... (attempt {attempt + 1}/{max_retries})"
                        )
                        time.sleep(self.request_delay * 2)
                        continue
                    return None, None

                with session as s:
                    logger.info(f"Requesting CAAML data with query: {query_string}")
                    self._enforce_rate_limit()
                    query_response = s.get(self.caaml_query_url + query_string)

                    # Debug logging
                    logger.debug(f"Query response status: {query_response.status_code}")
                    logger.debug(
                        f"Query response headers: {dict(query_response.headers)}"
                    )

                    # Check for Content-Disposition header and success status
                    content_disposition = query_response.headers.get(
                        "Content-Disposition", None
                    )

                    if (
                        content_disposition is not None
                        and query_response.status_code == 200
                    ):
                        # Extract filename from Content-Disposition header
                        try:
                            match = re.search(
                                r'filename="([^"]+)"', content_disposition
                            )
                            if not match:
                                logger.error(
                                    f"Could not parse filename from Content-Disposition: '{content_disposition}'"
                                )
                                return None, None

                            full_filename = match.group(1)

                            # Check if we got an empty result
                            if full_filename == "_caaml.tar.gz":
                                logger.info(
                                    "No data available for the requested query - server returned empty filename"
                                )
                                return None, None

                            # Remove the _caaml suffix if present
                            filename = full_filename.replace("_caaml", "")

                            # Final validation
                            if not filename or filename == ".tar.gz":
                                logger.error(
                                    f"Invalid filename extracted from Content-Disposition: '{content_disposition}'"
                                )
                                return None, None

                            file_url = self.data_url + filename

                            # Download the actual file
                            logger.info(f"Downloading CAAML file from: {file_url}")
                            file_response = s.get(file_url)

                            if file_response.status_code == 200:
                                logger.info(f"CAAML download successful: {filename}")
                                return file_response.content, filename
                            else:
                                logger.warning(
                                    f"File download failed with status {file_response.status_code}"
                                )
                                if file_response.status_code == 403:
                                    logger.error(
                                        "403 Forbidden - possible rate limiting or authentication issue"
                                    )
                                    if attempt < max_retries - 1:
                                        logger.info(
                                            f"Retrying after 403 error... (attempt {attempt + 1}/{max_retries})"
                                        )
                                        time.sleep(self.request_delay * 3)
                                        continue
                                return None, None
                        except Exception as e:
                            logger.error(
                                f"Error parsing Content-Disposition header '{content_disposition}': {e}"
                            )
                            return None, None
                    else:
                        if query_response.status_code == 403:
                            logger.error(
                                "403 Forbidden - possible rate limiting or authentication issue"
                            )
                            if attempt < max_retries - 1:
                                logger.info(
                                    f"Retrying after 403 error... (attempt {attempt + 1}/{max_retries})"
                                )
                                time.sleep(self.request_delay * 3)
                                continue
                        elif query_response.status_code == 500:
                            logger.error(
                                "Server error (500) - this may indicate an issue with the query parameters or server"
                            )
                        elif content_disposition is None:
                            logger.error(
                                "No Content-Disposition header found - query may have returned no results"
                            )
                        return None, None

            except requests.RequestException as e:
                logger.error(f"CAAML request error: {e}")
                if attempt < max_retries - 1:
                    logger.info(
                        f"Retrying after request exception... (attempt {attempt + 1}/{max_retries})"
                    )
                    time.sleep(self.request_delay * 2)
                    continue
                return None, None

        # If we get here, all retries failed
        logger.error(f"Failed to make CAAML request after {max_retries} attempts")
        return None, None

    def download_caaml_data(
        self, query_string: str, max_retries: int = 3
    ) -> Optional[bytes]:
        """Download CAAML data from snowpilot.org"""
        data, filename = self._make_caaml_request(query_string, max_retries)
        return data

    def estimate_pit_count(self, query_string: str, max_retries: int = 3) -> int:
        """
        Estimate the number of pits for a query by downloading and counting files

        Note: This downloads the actual data to count files. The snowpilot.org API
        doesn't provide a metadata endpoint for counts without downloading.

        Args:
            query_string: The query string to estimate
            max_retries: Maximum number of retry attempts

        Returns:
            Number of pits that would be downloaded (0 if failed or no data)
        """
        data, filename = self._make_caaml_request(query_string, max_retries)

        if not data:
            return 0

        # Extract and count CAAML files
        try:
            with tempfile.NamedTemporaryFile(
                suffix=".tar.gz", delete=False
            ) as temp_file:
                temp_file.write(data)
                temp_file_path = temp_file.name

            # Extract and count CAAML files
            extract_path = temp_file_path.replace(".tar.gz", "")
            with tarfile.open(temp_file_path, "r:gz") as tar:
                tar.extractall(path=extract_path)

            # Count CAAML files
            pit_count = 0
            for root, dirs, files in os.walk(extract_path):
                for file in files:
                    if file.endswith("caaml.xml"):
                        pit_count += 1

            # Clean up temporary files
            shutil.rmtree(extract_path, ignore_errors=True)
            os.remove(temp_file_path)

            logger.info(f"Estimated {pit_count} pits for query")
            return pit_count

        except Exception as e:
            logger.error(f"Error during pit count estimation: {e}")
            # Clean up on error
            try:
                shutil.rmtree(extract_path, ignore_errors=True)
                os.remove(temp_file_path)
            except:
                pass
            return 0


class QueryEngine:
    """Main query engine for snowpilot.org CAAML data with automatic large dataset handling"""

    def __init__(self, pits_path: str = DEFAULT_PITS_PATH):
        self.pits_path = pits_path
        self.session = SnowPilotSession()
        self.query_builder = QueryBuilder()
        self.progress_tracker = None
        os.makedirs(self.pits_path, exist_ok=True)

    def _load_progress(self, progress_file: Path) -> ProgressTracker:
        """Load progress from file"""
        if progress_file.exists():
            try:
                with open(progress_file, "r") as f:
                    data = json.load(f)
                    return ProgressTracker(
                        completed_chunks=data.get("completed_chunks", []),
                        failed_chunks=data.get("failed_chunks", []),
                        total_pits=data.get("total_pits", 0),
                        start_time=data.get("start_time"),
                        last_update=data.get("last_update"),
                        chunk_results=data.get("chunk_results", []),
                    )
            except Exception as e:
                logger.warning(f"Could not load progress file: {e}")

        return ProgressTracker()

    def _save_progress(self, progress_file: Path, progress: ProgressTracker):
        """Save progress to file"""
        progress.last_update = datetime.now().isoformat()
        try:
            with open(progress_file, "w") as f:
                json.dump(
                    {
                        "completed_chunks": progress.completed_chunks,
                        "failed_chunks": progress.failed_chunks,
                        "total_pits": progress.total_pits,
                        "start_time": progress.start_time,
                        "last_update": progress.last_update,
                        "chunk_results": progress.chunk_results,
                    },
                    f,
                    indent=2,
                )
        except Exception as e:
            logger.warning(f"Could not save progress file: {e}")

    def _generate_date_chunks(
        self, start_date: str, end_date: str, chunk_size_days: int
    ) -> List[tuple]:
        """Generate date chunks for large dataset handling"""
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

    def _should_chunk_query(self, query_filter: QueryFilter) -> bool:
        """Determine if a query should be chunked based on user configuration"""
        return query_filter.chunk

    def dry_run(self, query_filter: QueryFilter) -> DryRunResult:
        """
        Perform a dry run to see how many chunks will be run and pits per chunk

        Args:
            query_filter: Filter parameters for the query

        Returns:
            DryRunResult containing detailed chunk information
        """
        logger.info(f"Performing dry run with filter: {query_filter}")

        # Validate and set default date range if not provided
        query_filter = self._validate_and_set_dates(query_filter)

        # Check if this will be chunked
        will_be_chunked = self._should_chunk_query(query_filter)

        if not will_be_chunked:
            # Single request - get count directly
            query_string = self.query_builder.build_caaml_query(query_filter)
            estimated_count = self.session.estimate_pit_count(query_string)

            return DryRunResult(
                query_filter=query_filter,
                total_estimated_pits=estimated_count,
                will_be_chunked=False,
                chunk_size_days=0,
                chunk_details=[],
            )

        # Chunked request - check each chunk individually
        chunks = self._generate_date_chunks(
            query_filter.date_start,
            query_filter.date_end,
            query_filter.chunk_size_days,
        )

        logger.info(f"Chunked query will use {len(chunks)} chunks")

        chunk_details = []

        for i, (chunk_start, chunk_end) in enumerate(chunks):
            chunk_id = f"{chunk_start}_{chunk_end}"

            # Create chunk info
            chunk_info = ChunkInfo(
                chunk_id=chunk_id,
                start_date=chunk_start,
                end_date=chunk_end,
            )

            chunk_details.append(chunk_info)

            logger.info(f"Chunk {i + 1}/{len(chunks)}: {chunk_start} to {chunk_end}")

        # Get overall estimate for the full query
        query_string = self.query_builder.build_caaml_query(query_filter)
        total_estimated_pits = self.session.estimate_pit_count(query_string)

        return DryRunResult(
            query_filter=query_filter,
            total_estimated_pits=total_estimated_pits,
            will_be_chunked=True,
            chunk_size_days=query_filter.chunk_size_days,
            chunk_details=chunk_details,
        )

    def _convert_to_date_string(self, date_input: Union[str, datetime, Any]) -> str:
        """
        Convert various date input types to YYYY-MM-DD string format

        Args:
            date_input: Date as string, datetime, or datetime-like object (e.g. pandas Timestamp)

        Returns:
            Date string in YYYY-MM-DD format
        """
        if date_input is None:
            return None

        if isinstance(date_input, str):
            # Validate string format
            try:
                datetime.strptime(date_input, "%Y-%m-%d")
                return date_input
            except ValueError:
                raise ValueError(
                    f"Invalid date string format: {date_input}. Use YYYY-MM-DD format."
                )

        # Handle datetime-like objects
        if hasattr(date_input, "strftime"):
            # This covers datetime, pandas Timestamp, and other datetime-like objects
            return date_input.strftime("%Y-%m-%d")

        # Handle objects that can be converted to datetime
        if hasattr(date_input, "date"):
            return date_input.date().strftime("%Y-%m-%d")

        # Try to convert to string and parse
        try:
            date_str = str(date_input)
            if " " in date_str:
                # If it contains time info, split and take date part
                date_str = date_str.split(" ")[0]
            datetime.strptime(date_str, "%Y-%m-%d")
            return date_str
        except (ValueError, TypeError):
            raise ValueError(
                f"Cannot convert {type(date_input).__name__} to date string: {date_input}"
            )

    def _validate_and_set_dates(self, query_filter: QueryFilter) -> QueryFilter:
        """
        Validate and set default date range if not provided

        Args:
            query_filter: Filter parameters for the query

        Returns:
            Updated QueryFilter with validated dates
        """
        # Set default date range if not provided
        if not query_filter.date_start:
            query_filter.date_start = (datetime.now() - timedelta(days=7)).strftime(
                "%Y-%m-%d"
            )
        if not query_filter.date_end:
            query_filter.date_end = datetime.now().strftime("%Y-%m-%d")

        # Convert inputs to string format
        query_filter.date_start = self._convert_to_date_string(query_filter.date_start)
        query_filter.date_end = self._convert_to_date_string(query_filter.date_end)

        # Validate date formats and convert to datetime objects for comparison
        try:
            start_date = datetime.strptime(query_filter.date_start, "%Y-%m-%d")
            end_date = datetime.strptime(query_filter.date_end, "%Y-%m-%d")
        except ValueError as e:
            raise ValueError(f"Invalid date format. Use YYYY-MM-DD format. Error: {e}")

        # Check if start date is before end date
        if start_date > end_date:
            raise ValueError(
                f"Start date ({query_filter.date_start}) must be before end date ({query_filter.date_end})"
            )

        # Check if dates are too far in the future
        today = datetime.now().date()
        if start_date.date() > today:
            logger.warning(
                f"Start date ({query_filter.date_start}) is in the future. Snowpilot.org may not have data for future dates."
            )
        if end_date.date() > today:
            logger.warning(
                f"End date ({query_filter.date_end}) is in the future. Snowpilot.org may not have data for future dates."
            )

        # Check if date range is too large (more than 2 years)
        if (end_date - start_date).days > 730:
            logger.warning(
                f"Date range is very large ({(end_date - start_date).days} days). This may result in a very large download."
            )

        return query_filter

    def query_pits(
        self,
        query_filter: QueryFilter,
        auto_approve: bool = False,
        approval_threshold: int = 100,
    ) -> QueryResult:
        """
        Query snow pits from snowpilot.org in CAAML format with automatic large dataset handling

        Args:
            query_filter: Filter parameters for the query
            auto_approve: If True, skip approval prompt
            approval_threshold: Number of pits above which approval is required

        Returns:
            QueryResult containing snow pit data
        """
        logger.info(f"Querying CAAML pits with filter: {query_filter}")

        # Validate and set default date range if not provided
        query_filter = self._validate_and_set_dates(query_filter)

        # Check if this should be chunked
        should_chunk = self._should_chunk_query(query_filter)

        if should_chunk:
            logger.info("Using chunked download approach")
            return self._query_chunked(query_filter, auto_approve, approval_threshold)
        else:
            logger.info("Small dataset, using standard download approach")
            return self._query_standard(query_filter, auto_approve, approval_threshold)

    def _query_standard(
        self, query_filter: QueryFilter, auto_approve: bool, approval_threshold: int
    ) -> QueryResult:
        """Standard query for small datasets"""
        # Get dry run first
        dry_run_result = self.dry_run(query_filter)

        # Check if approval is needed
        if (
            not auto_approve
            and dry_run_result.total_estimated_pits > approval_threshold
        ):
            print(f"\n{dry_run_result}")
            print(
                f"\nThis query will download approximately {dry_run_result.total_estimated_pits} pits."
            )

            if dry_run_result.total_estimated_pits > 1000:
                print(
                    "⚠️  WARNING: This is a large download that may take significant time and bandwidth."
                )

            response = (
                input("\nDo you want to proceed with the download? (y/N): ")
                .lower()
                .strip()
            )

            if response not in ["y", "yes"]:
                logger.info("Download cancelled by user")
                result = QueryResult(
                    query_filter=query_filter, dry_run_result=dry_run_result
                )
                result.download_info["status"] = "cancelled"
                result.download_info["reason"] = "User cancelled download"
                return result
        elif not auto_approve:
            print(
                f"Dry run: Will download approximately {dry_run_result.total_estimated_pits} pits"
            )

        # Execute the CAAML query
        result = self._query_caaml(query_filter)

        # Add dry run info to result
        result.dry_run_result = dry_run_result
        return result

    def _query_chunked(
        self, query_filter: QueryFilter, auto_approve: bool, approval_threshold: int
    ) -> QueryResult:
        """Chunked query for large datasets"""
        # Get dry run first
        dry_run_result = self.dry_run(query_filter)

        # Check if approval is needed
        if (
            not auto_approve
            and dry_run_result.total_estimated_pits > approval_threshold
        ):
            print(f"\n{dry_run_result}")
            print(
                f"\nThis query will download approximately {dry_run_result.total_estimated_pits} pits "
                f"using {len(dry_run_result.chunk_details)} chunks."
            )

            if dry_run_result.total_estimated_pits > 1000:
                print(
                    "⚠️  WARNING: This is a large download that may take significant time and bandwidth."
                )

            response = (
                input("\nDo you want to proceed with the chunked download? (y/N): ")
                .lower()
                .strip()
            )

            if response not in ["y", "yes"]:
                logger.info("Download cancelled by user")
                result = QueryResult(
                    query_filter=query_filter,
                    dry_run_result=dry_run_result,
                    was_chunked=True,
                )
                result.download_info["status"] = "cancelled"
                result.download_info["reason"] = "User cancelled download"
                return result
        elif not auto_approve:
            print(
                f"Dry run: Will download approximately {dry_run_result.total_estimated_pits} pits "
                f"using {len(dry_run_result.chunk_details)} chunks"
            )

        # Execute the chunked download
        result = self._download_chunked_dataset(query_filter)

        # Add dry run info to result
        result.dry_run_result = dry_run_result
        result.was_chunked = True
        return result

    def _download_chunked_dataset(self, query_filter: QueryFilter) -> QueryResult:
        """Download dataset using chunking approach"""
        # Validate that date range is provided for chunking
        if not query_filter.date_start or not query_filter.date_end:
            raise ValueError(
                "Date range (date_start and date_end) must be provided when chunking is enabled"
            )

        # Generate date chunks
        chunks = self._generate_date_chunks(
            query_filter.date_start, query_filter.date_end, query_filter.chunk_size_days
        )

        # Setup progress tracking
        progress_file = Path(self.pits_path) / "download_progress.json"
        progress = self._load_progress(progress_file)

        if not progress.start_time:
            progress.start_time = datetime.now().isoformat()

        # Filter out already completed chunks
        remaining_chunks = [
            chunk
            for chunk in chunks
            if f"{chunk[0]}_{chunk[1]}" not in progress.completed_chunks
        ]

        logger.info(
            f"Starting chunked download: {len(chunks)} total chunks, {len(remaining_chunks)} remaining"
        )

        result = QueryResult(query_filter=query_filter, was_chunked=True)
        all_pits = []

        # Process each chunk
        for i, (chunk_start, chunk_end) in enumerate(remaining_chunks):
            chunk_id = f"{chunk_start}_{chunk_end}"

            logger.info(f"Processing chunk {i + 1}/{len(remaining_chunks)}: {chunk_id}")

            # Skip if already completed
            if chunk_id in progress.completed_chunks:
                logger.info(f"Chunk {chunk_id} already completed, skipping")
                continue

            # Create chunk-specific query filter
            chunk_filter = QueryFilter(
                date_start=chunk_start,
                date_end=chunk_end,
                state=query_filter.state,
                username=query_filter.username,
                organization_name=query_filter.organization_name,
                per_page=query_filter.per_page,
                chunk=False,  # Don't chunk chunks
            )

            # Retry logic for failed chunks
            chunk_success = False
            for attempt in range(query_filter.max_retries):
                try:
                    chunk_result = self._query_caaml(chunk_filter)

                    if chunk_result.status == "success":
                        all_pits.extend(chunk_result.snow_pits)

                        # Track chunk results
                        chunk_info = {
                            "chunk_id": chunk_id,
                            "start_date": chunk_start,
                            "end_date": chunk_end,
                            "pits_count": len(chunk_result.snow_pits),
                            "success": True,
                        }
                        progress.chunk_results.append(chunk_info)
                        result.chunk_results.append(chunk_info)

                        progress.completed_chunks.append(chunk_id)
                        progress.total_pits += len(chunk_result.snow_pits)

                        # Remove from failed chunks if it was there
                        if chunk_id in progress.failed_chunks:
                            progress.failed_chunks.remove(chunk_id)

                        chunk_success = True
                        logger.info(
                            f"Chunk {chunk_id} completed successfully: {len(chunk_result.snow_pits)} pits"
                        )
                        break
                    elif chunk_result.status == "no_data":
                        # Legitimate case of no data for this chunk
                        logger.info(f"Chunk {chunk_id} returned no pits")

                        # Track chunk results
                        chunk_info = {
                            "chunk_id": chunk_id,
                            "start_date": chunk_start,
                            "end_date": chunk_end,
                            "pits_count": 0,
                            "success": True,
                        }
                        progress.chunk_results.append(chunk_info)
                        result.chunk_results.append(chunk_info)

                        progress.completed_chunks.append(chunk_id)
                        chunk_success = True
                        break
                    else:
                        # Failed chunk - treat as failure and retry
                        error_msg = chunk_result.error_message or "Unknown error"
                        logger.error(f"Chunk {chunk_id} failed: {error_msg}")

                        # Don't break here - let it retry
                        if attempt < query_filter.max_retries - 1:
                            delay = 30 * (attempt + 1)
                            logger.info(
                                f"Retrying chunk {chunk_id} in {delay} seconds..."
                            )
                            time.sleep(delay)
                            continue
                        else:
                            # Final failure after all retries
                            logger.error(
                                f"Chunk {chunk_id} failed after {query_filter.max_retries} attempts"
                            )
                            if chunk_id not in progress.failed_chunks:
                                progress.failed_chunks.append(chunk_id)
                            break

                except Exception as e:
                    logger.error(
                        f"Chunk {chunk_id} attempt {attempt + 1} failed with exception: {e}"
                    )

                    if attempt < query_filter.max_retries - 1:
                        delay = 30 * (attempt + 1)
                        logger.info(f"Retrying chunk {chunk_id} in {delay} seconds...")
                        time.sleep(delay)
                    else:
                        logger.error(
                            f"Chunk {chunk_id} failed after {query_filter.max_retries} attempts"
                        )
                        if chunk_id not in progress.failed_chunks:
                            progress.failed_chunks.append(chunk_id)

            # Save progress after each chunk
            self._save_progress(progress_file, progress)

            # Show overall progress
            completed = len(progress.completed_chunks)
            total = len(chunks)
            progress_pct = (completed / total) * 100
            logger.info(
                f"Overall progress: {completed}/{total} chunks ({progress_pct:.1f}%)"
            )
            logger.info(f"Total pits downloaded: {progress.total_pits}")

        # Finalize result
        result.snow_pits = all_pits
        result.total_count = len(all_pits)
        result.download_info = {
            "chunked": True,
            "total_chunks": len(chunks),
            "completed_chunks": len(progress.completed_chunks),
            "failed_chunks": len(progress.failed_chunks),
            "chunk_results": progress.chunk_results,
        }

        # Print final summary
        self._print_chunked_summary(progress, len(chunks))

        return result

    def _print_chunked_summary(self, progress: ProgressTracker, total_chunks: int):
        """Print final summary for chunked downloads"""
        print("\n" + "=" * 60)
        print("📊 CHUNKED DOWNLOAD SUMMARY")
        print("=" * 60)

        completed = len(progress.completed_chunks)
        failed = len(progress.failed_chunks)

        print(f"✅ Completed chunks: {completed}/{total_chunks}")
        print(f"❌ Failed chunks: {failed}")
        print(f"📊 Total pits downloaded: {progress.total_pits}")

        if progress.start_time:
            start_time = datetime.fromisoformat(progress.start_time)
            duration = datetime.now() - start_time
            print(f"⏱️  Total time: {duration}")

        if failed > 0:
            print(f"\n❌ Failed chunks ({failed}):")
            for chunk_id in progress.failed_chunks:
                print(f"  - {chunk_id}")
            print("\n💡 You can re-run this query to retry failed chunks")

    def _query_caaml(self, query_filter: QueryFilter) -> QueryResult:
        """Query CAAML data from snowpilot.org (handles multiple requests if needed)"""
        result = QueryResult(query_filter=query_filter)
        all_extracted_files = []
        saved_files = []
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Try to download with current per_page setting
        query_string = self.query_builder.build_caaml_query(query_filter)
        caaml_data = self.session.download_caaml_data(query_string)

        if caaml_data:
            # Save CAAML data to file
            filename = f"{query_filter.date_start}_{query_filter.date_end}_{timestamp}_pits.tar.gz"
            filepath = os.path.join(self.pits_path, filename)

            with open(filepath, "wb") as f:
                f.write(caaml_data)

            saved_files.append(filepath)

            # Extract and collect CAAML files
            extracted_files = self._extract_caaml_files(filepath)
            all_extracted_files.extend(extracted_files)

            # Check if we got exactly per_page pits, which might indicate there are more
            if len(extracted_files) == query_filter.per_page:
                logger.info(
                    f"Got {len(extracted_files)} pits (exactly per_page={query_filter.per_page}), checking if there are more..."
                )

                # Try with a larger per_page to get remaining pits
                larger_filter = QueryFilter(
                    date_start=query_filter.date_start,
                    date_end=query_filter.date_end,
                    state=query_filter.state,
                    per_page=RESULTS_PER_PAGE,  # Try larger batch
                )
                larger_query_string = self.query_builder.build_caaml_query(
                    larger_filter
                )
                additional_data = self.session.download_caaml_data(larger_query_string)

                if (
                    additional_data and additional_data != caaml_data
                ):  # Make sure it's different data
                    filename2 = f"{query_filter.date_start}_{query_filter.date_end}_{timestamp}_additional_pits.tar.gz"
                    filepath2 = os.path.join(self.pits_path, filename2)

                    with open(filepath2, "wb") as f:
                        f.write(additional_data)

                    saved_files.append(filepath2)
                    additional_files = self._extract_caaml_files(filepath2)

                    # Only add files that we haven't already processed
                    existing_ids = set()
                    for existing_file in all_extracted_files:
                        try:
                            # Extract pit ID from filename
                            pit_id = os.path.basename(existing_file).split("-")[-2]
                            existing_ids.add(pit_id)
                        except:
                            pass

                    new_files = []
                    for new_file in additional_files:
                        try:
                            pit_id = os.path.basename(new_file).split("-")[-2]
                            if pit_id not in existing_ids:
                                new_files.append(new_file)
                        except:
                            new_files.append(new_file)  # Include if we can't parse ID

                    all_extracted_files.extend(new_files)
                    logger.info(f"Found {len(new_files)} additional unique pits")

            if saved_files:
                result.download_info["saved_files"] = saved_files
            result.download_info["format"] = "caaml"

            # Parse all CAAML files
            result.snow_pits = self._parse_caaml_pits(all_extracted_files, query_filter)
            result.total_count = len(result.snow_pits)

            logger.info(
                f"Downloaded {result.total_count} pits total from {len(saved_files)} archives"
            )

            # Set status based on results
            if result.total_count > 0:
                result.status = "success"
            else:
                result.status = "no_data"
        else:
            # No data received - this could be due to server error or no data available
            result.status = "failed"
            result.error_message = "No data received from server (possible server error or no data available)"

        return result

    def _extract_caaml_files(self, archive_path: str) -> List[str]:
        """Extract CAAML files from tar.gz archive"""
        extract_path = archive_path.replace(".tar.gz", "")

        try:
            # Extract the tar.gz file
            with tarfile.open(archive_path, "r:gz") as tar:
                tar.extractall(path=extract_path)

            # Find all CAAML XML files
            caaml_files = []
            for root, dirs, files in os.walk(extract_path):
                for file in files:
                    if file.endswith("caaml.xml"):
                        caaml_files.append(os.path.join(root, file))

            logger.info(f"Extracted {len(caaml_files)} CAAML files from {archive_path}")

            # Clean up - remove the archive but keep extracted files for now
            os.remove(archive_path)

            return caaml_files

        except Exception as e:
            logger.error(f"Error extracting CAAML files: {e}")
            return []

    def _parse_caaml_pits(
        self, caaml_files: List[str], query_filter: QueryFilter
    ) -> List[SnowPit]:
        """Parse individual CAAML files"""
        pits = []

        for file_path in caaml_files:
            try:
                pit = caaml_parser(file_path)
                pits.append(pit)
            except Exception as e:
                logger.error(f"Error parsing CAAML file {file_path}: {e}")
                continue

        logger.info(f"Parsed {len(pits)} pits from {len(caaml_files)} files")
        return pits

    def search_local_pits(self, query_filter: QueryFilter) -> QueryResult:
        """Search locally saved pit files"""
        result = QueryResult(query_filter=query_filter)

        # Find all local CAAML files
        caaml_files = glob(
            os.path.join(self.pits_path, "**", "*caaml.xml"), recursive=True
        )

        if caaml_files:
            result.snow_pits = self._parse_caaml_pits(caaml_files, query_filter)
            result.total_count = len(result.snow_pits)
            result.download_info["source"] = "local"
            result.download_info["files_searched"] = len(caaml_files)

        return result

    def download_results(
        self,
        query_filter: QueryFilter,
        auto_approve: bool = False,
        approval_threshold: int = 100,
    ) -> QueryResult:
        """
        Download snow pit data for any query filter - handles all dataset sizes uniformly

        This method replaces the old download_large_dataset function and provides a unified
        interface for downloading data regardless of dataset size. It automatically handles
        chunking, multi-state queries, and progress tracking as needed.

        Args:
            query_filter: Filter parameters for the query
            auto_approve: If True, skip approval prompt
            approval_threshold: Number of pits above which approval is required

        Returns:
            QueryResult containing snow pit data

        Examples:
            # Single state query
            query_filter = QueryFilter(
                date_start="2023-01-01",
                date_end="2023-01-31",
                state="MT",
                chunk=True,
                chunk_size_days=7
            )
            result = engine.download_results(query_filter)

            # Multi-state query
            query_filter = QueryFilter(
                date_start="2023-01-01",
                date_end="2023-01-31",
                states=["MT", "CO", "WY"],
                chunk=True,
                chunk_size_days=7
            )
            result = engine.download_results(query_filter)
        """
        logger.info(f"Starting download with filter: {query_filter}")

        # Handle multi-state queries if states list is provided
        if hasattr(query_filter, "states") and query_filter.states:
            return self._download_multi_state_results(
                query_filter, auto_approve, approval_threshold
            )

        # Single state or no state specified - use standard query
        return self.query_pits(query_filter, auto_approve, approval_threshold)

    def _download_multi_state_results(
        self,
        query_filter: QueryFilter,
        auto_approve: bool = False,
        approval_threshold: int = 100,
    ) -> QueryResult:
        """
        Download results for multiple states uniformly

        Args:
            query_filter: Filter parameters with states list
            auto_approve: If True, skip approval prompt
            approval_threshold: Number of pits above which approval is required

        Returns:
            QueryResult containing combined data from all states
        """
        states = (
            query_filter.states
            if hasattr(query_filter, "states")
            else [query_filter.state]
        )

        # Get dry run estimate for all states combined
        total_estimated_pits = 0
        for state in states:
            state_filter = QueryFilter(
                pit_name=query_filter.pit_name,
                date_start=query_filter.date_start,
                date_end=query_filter.date_end,
                state=state,
                username=query_filter.username,
                organization_name=query_filter.organization_name,
                per_page=query_filter.per_page,
                chunk=query_filter.chunk,
                chunk_size_days=query_filter.chunk_size_days,
                max_retries=query_filter.max_retries,
            )
            dry_run = self.dry_run(state_filter)
            total_estimated_pits += dry_run.total_estimated_pits

        # Check if approval is needed for the combined total
        if not auto_approve and total_estimated_pits > approval_threshold:
            print(f"\nMulti-state download summary:")
            print(f"  States: {', '.join(states)}")
            print(f"  Date range: {query_filter.date_start} to {query_filter.date_end}")
            print(f"  Total estimated pits: {total_estimated_pits}")

            if query_filter.chunk:
                print(f"  Will use chunking: {query_filter.chunk_size_days} day chunks")

            if total_estimated_pits > 1000:
                print(
                    "⚠️  WARNING: This is a large download that may take significant time and bandwidth."
                )

            response = (
                input(
                    f"\nDo you want to proceed with downloading {total_estimated_pits} pits from {len(states)} states? (y/N): "
                )
                .lower()
                .strip()
            )

            if response not in ["y", "yes"]:
                logger.info("Download cancelled by user")
                result = QueryResult(
                    query_filter=query_filter,
                    was_chunked=query_filter.chunk,
                )
                result.download_info["status"] = "cancelled"
                result.download_info["reason"] = "User cancelled multi-state download"
                return result

        # Download data for each state
        all_pits = []
        all_chunk_results = []
        successful_states = []
        failed_states = []

        for state in states:
            logger.info(f"Downloading data for state: {state}")

            state_filter = QueryFilter(
                pit_name=query_filter.pit_name,
                date_start=query_filter.date_start,
                date_end=query_filter.date_end,
                state=state,
                username=query_filter.username,
                organization_name=query_filter.organization_name,
                per_page=query_filter.per_page,
                chunk=query_filter.chunk,
                chunk_size_days=query_filter.chunk_size_days,
                max_retries=query_filter.max_retries,
            )

            try:
                state_result = self.query_pits(state_filter, auto_approve=True)
                all_pits.extend(state_result.snow_pits)

                if state_result.chunk_results:
                    all_chunk_results.extend(state_result.chunk_results)

                successful_states.append(state)
                logger.info(
                    f"State {state} completed: {len(state_result.snow_pits)} pits"
                )

            except Exception as e:
                logger.error(f"Failed to download data for state {state}: {e}")
                failed_states.append(state)
                continue

        # Create combined result
        result = QueryResult(
            snow_pits=all_pits,
            total_count=len(all_pits),
            query_filter=query_filter,
            chunk_results=all_chunk_results,
            was_chunked=query_filter.chunk,
        )

        result.download_info = {
            "multi_state": True,
            "total_states": len(states),
            "successful_states": len(successful_states),
            "failed_states": len(failed_states),
            "states_processed": successful_states,
            "states_failed": failed_states,
            "total_pits": len(all_pits),
            "chunked": query_filter.chunk,
        }

        # Print summary
        print(f"\n{'=' * 60}")
        print("📊 MULTI-STATE DOWNLOAD SUMMARY")
        print(f"{'=' * 60}")
        print(f"✅ Successful states: {len(successful_states)}/{len(states)}")
        if successful_states:
            print(f"   States: {', '.join(successful_states)}")
        if failed_states:
            print(f"❌ Failed states: {len(failed_states)}")
            print(f"   States: {', '.join(failed_states)}")
        print(f"📊 Total pits downloaded: {len(all_pits)}")
        print(f"⏱️  Date range: {query_filter.date_start} to {query_filter.date_end}")
        if query_filter.chunk:
            print(f"📦 Used chunking: {query_filter.chunk_size_days} day chunks")

        return result


# Example usage showing the flexible QueryFilter API:
"""
Common Usage Examples:

# Basic single state query
engine = QueryEngine()
query_filter = QueryFilter(
    date_start="2023-01-01",
    date_end="2023-01-31",
    state="MT"
)
result = engine.download_results(query_filter)

# Organization-specific query with date range
query_filter = QueryFilter(
    organization_name="Bridger Bowl Ski Patrol",
    date_start="2023-01-01",
    date_end="2023-01-31",
    state="MT"
)
result = engine.download_results(query_filter)

# Username query with multiple filters
query_filter = QueryFilter(
    username="john_doe",
    date_start="2023-01-01",
    date_end="2023-01-31",
    state="MT",
    organization_name="Bridger Bowl Ski Patrol"
)
result = engine.download_results(query_filter)

# Large dataset with chunking (single state)
query_filter = QueryFilter(
    date_start="2019-01-01",
    date_end="2024-01-31",
    state="MT",
    chunk=True,
    chunk_size_days=30
)
result = engine.download_results(query_filter, auto_approve=True)

# Multi-state query with chunking
query_filter = QueryFilter(
    date_start="2023-01-01",
    date_end="2023-12-31",
    states=["MT", "CO", "WY"],
    chunk=True,
    chunk_size_days=7
)
result = engine.download_results(query_filter)

# All supported states for large dataset
all_states = ["MT", "CO", "WY", "UT", "ID", "WA", "OR", "CA", "AK", "NH", "VT", "ME", "NY"]
query_filter = QueryFilter(
    date_start="2023-01-01",
    date_end="2023-12-31",
    states=all_states,
    chunk=True,
    chunk_size_days=7
)
result = engine.download_results(query_filter, auto_approve=True)

# Dry run to see what would be downloaded
dry_run_result = engine.dry_run(query_filter)
print(dry_run_result)
"""
