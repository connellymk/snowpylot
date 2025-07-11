"""
Query Engine for SnowPilot.org CAAML Data

This module provides tools for downloading and querying CAAML snow pit data
from snowpilot.org with flexible filtering capabilities.
"""

import json
import logging
import os
import shutil
import tarfile
from datetime import datetime, timedelta
from glob import glob
from typing import Dict, List, Optional, Union, Any
from dataclasses import dataclass, field

import requests

from .caaml_parser import caaml_parser
from .snow_pit import SnowPit

# Configuration constants
DEFAULT_PITS_PATH = "data/snowpits"

# Create basic logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class QueryFilter:
    """Data class for query filter parameters"""

    pit_id: Optional[str] = None
    pit_name: Optional[str] = None
    date_start: Optional[str] = None  # Format: YYYY-MM-DD
    date_end: Optional[str] = None  # Format: YYYY-MM-DD
    country: Optional[str] = None
    state: Optional[str] = None
    region: Optional[str] = None
    user_id: Optional[str] = None
    username: Optional[str] = None
    organization_id: Optional[str] = None
    organization_name: Optional[str] = None
    elevation_min: Optional[float] = None
    elevation_max: Optional[float] = None
    aspect: Optional[str] = None
    per_page: int = 100  # Default to 100 for CAAML queries


@dataclass
class QueryPreview:
    """Data class for query preview information"""

    estimated_count: int = 0
    query_filter: Optional[QueryFilter] = None
    preview_info: Dict[str, Any] = field(default_factory=dict)

    def __str__(self) -> str:
        """Return a formatted preview string"""
        return (
            f"Query Preview:\n"
            f"  Estimated pits: {self.estimated_count}\n"
            f"  Date range: {self.query_filter.date_start} to {self.query_filter.date_end}\n"
            f"  State: {self.query_filter.state or 'Any'}\n"
            f"  Username: {self.query_filter.username or 'Any'}\n"
            f"  Organization: {self.query_filter.organization_name or 'Any'}\n"
            f"  Elevation: {self.query_filter.elevation_min or 'Any'} - {self.query_filter.elevation_max or 'Any'}m\n"
            f"  Format: CAAML"
        )


@dataclass
class QueryResult:
    """Data class for query results"""

    snow_pits: List[SnowPit] = field(default_factory=list)
    total_count: int = 0
    query_filter: Optional[QueryFilter] = None
    download_info: Dict[str, Any] = field(default_factory=dict)
    preview: Optional[QueryPreview] = None


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
        """Build query string for CAAML endpoint using correct parameter format"""
        params = []

        # PIT_NAME parameter
        pit_name = query_filter.pit_name or ""
        params.append(f"PIT_NAME={pit_name}")

        # STATE parameter is required for snowpilot.org API
        if query_filter.state:
            if query_filter.state not in self.supported_states:
                raise ValueError(
                    f"State '{query_filter.state}' not supported. Supported states: {list(self.supported_states.keys())}"
                )
            params.append(f"STATE={query_filter.state}")
        else:
            # If no state specified, default to Montana (MT) as it has good data coverage
            logger.warning("No state specified, defaulting to Montana (MT)")
            params.append("STATE=MT")

        # Date parameters
        if query_filter.date_start:
            params.append(f"OBS_DATE_MIN={query_filter.date_start}")
        if query_filter.date_end:
            params.append(f"OBS_DATE_MAX={query_filter.date_end}")

        # Recent dates parameter (always 0 for custom date ranges)
        params.append("recent_dates=0")

        # USERNAME parameter
        username = query_filter.username or ""
        params.append(f"USERNAME={username}")

        # AFFIL parameter (organization/affiliation)
        affil = query_filter.organization_name or ""
        params.append(f"AFFIL={affil}")

        # Per page parameter
        params.append(f"per_page={query_filter.per_page}")

        # Advanced query parameter (empty for now)
        params.append("ADV_WHERE_QUERY=")

        # Submit parameter
        params.append("submit=Get%20Pits")

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

    def download_caaml_data(self, query_string: str) -> Optional[bytes]:
        """Download CAAML data from snowpilot.org"""
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

        try:
            # Create a fresh session context
            with requests.Session() as s:
                # Authenticate
                _ = s.post(self.login_url, data=payload)

                # Make the CAAML query request
                logger.info(f"Requesting CAAML data with query: {query_string}")
                query_response = s.post(self.caaml_query_url + query_string)

                # Check for Content-Disposition header and success status
                content_disposition = query_response.headers.get(
                    "Content-Disposition", None
                )
                if (
                    content_disposition is not None
                    and query_response.status_code == 200
                ):
                    # Extract filename from Content-Disposition header
                    # Format: attachment; filename="filename.tar.gz"
                    filename = content_disposition[22:-1].replace("_caaml", "")
                    file_url = self.data_url + filename

                    # Download the actual file
                    logger.info(f"Downloading CAAML file from: {file_url}")
                    file_response = s.get(file_url)
                    if file_response.status_code == 200:
                        logger.info(f"CAAML download successful: {filename}")
                        return file_response.content
                    else:
                        logger.warning(
                            f"File download failed with status {file_response.status_code}"
                        )
                        return None
                else:
                    logger.warning(
                        f"CAAML download failed with status {query_response.status_code}"
                    )
                    if query_response.status_code == 500:
                        logger.error(
                            "Server error (500) - this may indicate an issue with the query parameters or server"
                        )
                    return None

        except requests.RequestException as e:
            logger.error(f"CAAML download error: {e}")
            return None

    def preview_query(self, query_string: str) -> int:
        """
        Preview a query to get the estimated count of pits without downloading all data
        Uses a small per_page value to get a quick estimate

        Args:
            query_string: The query string to preview

        Returns:
            Estimated number of pits that would be downloaded
        """
        user = os.environ.get("SNOWPILOT_USER")
        password = os.environ.get("SNOWPILOT_PASSWORD")

        if not user or not password:
            logger.error(
                "SNOWPILOT_USER and SNOWPILOT_PASSWORD environment variables required"
            )
            return 0

        payload = {
            "name": user,
            "pass": password,
            "form_id": "user_login",
            "op": "Log in",
        }

        try:
            # Create a fresh session context
            with requests.Session() as s:
                # Authenticate
                _ = s.post(self.login_url, data=payload)

                # Modify query string to use per_page=1 for preview
                preview_query = query_string.replace(
                    f"per_page={query_string.split('per_page=')[1].split('&')[0]}",
                    "per_page=1",
                )

                logger.info(f"Previewing query: {preview_query}")
                response = s.post(self.caaml_query_url + preview_query)

                # Check if we got a successful response
                content_disposition = response.headers.get("Content-Disposition", None)
                if content_disposition is not None and response.status_code == 200:
                    # If we got a file, there's at least one pit
                    # Try with a slightly larger sample to get a better estimate
                    estimate_query = query_string.replace(
                        f"per_page={query_string.split('per_page=')[1].split('&')[0]}",
                        "per_page=10",
                    )

                    estimate_response = s.post(self.caaml_query_url + estimate_query)
                    if estimate_response.status_code == 200:
                        estimate_content_disposition = estimate_response.headers.get(
                            "Content-Disposition", None
                        )
                        if estimate_content_disposition is not None:
                            logger.info("Preview indicates data is available")
                            # For now, return a conservative estimate
                            # In a real implementation, we might try to download and count files
                            return 10  # Estimate based on per_page=10 request

                    return 1  # At least one pit available
                else:
                    logger.info(
                        f"Preview shows no data available (status: {response.status_code})"
                    )
                    return 0

        except requests.RequestException as e:
            logger.error(f"Preview request error: {e}")
            return 0


class QueryEngine:
    """Main query engine for snowpilot.org CAAML data"""

    def __init__(self, pits_path: str = DEFAULT_PITS_PATH):
        self.pits_path = pits_path
        self.session = SnowPilotSession()
        self.query_builder = QueryBuilder()
        os.makedirs(self.pits_path, exist_ok=True)

    def preview_query(self, query_filter: QueryFilter) -> QueryPreview:
        """
        Preview a query to see how many pits would be downloaded

        Args:
            query_filter: Filter parameters for the query

        Returns:
            QueryPreview containing estimated count and filter info
        """
        logger.info(f"Previewing query with filter: {query_filter}")

        # Validate and set default date range if not provided
        query_filter = self._validate_and_set_dates(query_filter)

        # Build query string for preview
        query_string = self.query_builder.build_caaml_query(query_filter)

        # Get estimated count
        estimated_count = self.session.preview_query(query_string)

        # Create preview object
        preview = QueryPreview(
            estimated_count=estimated_count,
            query_filter=query_filter,
            preview_info={"format": "CAAML", "query_string": query_string},
        )

        return preview

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

        # Validate date formats
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
        Query snow pits from snowpilot.org in CAAML format

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

        # Get preview first
        preview = self.preview_query(query_filter)

        # Check if approval is needed
        if not auto_approve and preview.estimated_count > approval_threshold:
            print(f"\n{preview}")
            print(
                f"\nThis query will download approximately {preview.estimated_count} pits."
            )

            if preview.estimated_count > 1000:
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
                result = QueryResult(query_filter=query_filter, preview=preview)
                result.download_info["status"] = "cancelled"
                result.download_info["reason"] = "User cancelled download"
                return result
        elif not auto_approve:
            print(
                f"Preview: Will download approximately {preview.estimated_count} pits"
            )

        # Execute the CAAML query
        result = self._query_caaml(query_filter)

        # Add preview info to result
        result.preview = preview
        return result

    def _query_caaml(self, query_filter: QueryFilter) -> QueryResult:
        """Query CAAML data from snowpilot.org"""
        query_string = self.query_builder.build_caaml_query(query_filter)
        caaml_data = self.session.download_caaml_data(query_string)

        result = QueryResult(query_filter=query_filter)

        if caaml_data:
            # Save CAAML data to file
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{query_filter.date_start}_{query_filter.date_end}_{timestamp}_pits.tar.gz"
            filepath = os.path.join(self.pits_path, filename)

            with open(filepath, "wb") as f:
                f.write(caaml_data)

            result.download_info["saved_file"] = filepath
            result.download_info["format"] = "caaml"

            # Extract and parse CAAML files
            extracted_files = self._extract_caaml_files(filepath)
            result.snow_pits = self._parse_caaml_pits(extracted_files, query_filter)
            result.total_count = len(result.snow_pits)

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
        """Parse individual CAAML files and apply filters"""
        pits = []

        for file_path in caaml_files:
            try:
                pit = caaml_parser(file_path)

                # Apply filters
                if self._matches_filter(pit, query_filter):
                    pits.append(pit)

            except Exception as e:
                logger.error(f"Error parsing CAAML file {file_path}: {e}")
                continue

        logger.info(
            f"Parsed and filtered {len(pits)} pits from {len(caaml_files)} files"
        )
        return pits

    def _matches_filter(self, pit: SnowPit, query_filter: QueryFilter) -> bool:
        """Check if a snow pit matches the query filter"""

        # Filter by pit ID
        if query_filter.pit_id and pit.core_info.pit_id != query_filter.pit_id:
            return False

        # Filter by pit name
        if (
            query_filter.pit_name
            and pit.core_info.pit_name
            and query_filter.pit_name.lower() not in pit.core_info.pit_name.lower()
        ):
            return False

        # Filter by country
        if (
            query_filter.country
            and pit.core_info.location.country
            and pit.core_info.location.country != query_filter.country
        ):
            return False

        # Filter by state/region
        if (
            query_filter.state
            and pit.core_info.location.region
            and pit.core_info.location.region != query_filter.state
        ):
            return False

        # Filter by username
        if (
            query_filter.username
            and pit.core_info.user.username
            and query_filter.username.lower() not in pit.core_info.user.username.lower()
        ):
            return False

        # Filter by organization name
        if (
            query_filter.organization_name
            and pit.core_info.user.operation_name
            and query_filter.organization_name.lower()
            not in pit.core_info.user.operation_name.lower()
        ):
            return False

        # Filter by elevation
        if pit.core_info.location.elevation:
            elevation = pit.core_info.location.elevation[0]
            if query_filter.elevation_min and elevation < query_filter.elevation_min:
                return False
            if query_filter.elevation_max and elevation > query_filter.elevation_max:
                return False

        # Filter by aspect
        if (
            query_filter.aspect
            and pit.core_info.location.aspect
            and pit.core_info.location.aspect != query_filter.aspect
        ):
            return False

        return True

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


# Convenience functions for common use cases
def preview_by_date_range(
    start_date: str, end_date: str, state: str = None
) -> QueryPreview:
    """
    Preview pits by date range

    Args:
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format
        state: State code (e.g. 'MT', 'CO', 'WY'). If None, defaults to 'MT'

    Returns:
        QueryPreview containing estimated count and filter info

    Example:
        preview = preview_by_date_range("2023-01-01", "2023-01-31", state="MT")
    """
    query_filter = QueryFilter(date_start=start_date, date_end=end_date, state=state)

    engine = QueryEngine()
    return engine.preview_query(query_filter)


def query_by_date_range(
    start_date: str, end_date: str, state: str = None, auto_approve: bool = False
) -> QueryResult:
    """
    Query pits by date range

    Args:
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format
        state: State code (e.g. 'MT', 'CO', 'WY'). If None, defaults to 'MT'
        auto_approve: If True, skip approval prompt

    Returns:
        QueryResult containing snow pit data

    Example:
        result = query_by_date_range("2023-01-01", "2023-01-31", state="MT")
    """
    query_filter = QueryFilter(date_start=start_date, date_end=end_date, state=state)

    engine = QueryEngine()
    return engine.query_pits(query_filter, auto_approve=auto_approve)


def query_by_pit_id(pit_id: str, auto_approve: bool = True) -> QueryResult:
    """Query a specific pit by ID (auto-approved by default for single pits)"""
    query_filter = QueryFilter(pit_id=pit_id)

    engine = QueryEngine()
    return engine.query_pits(query_filter, auto_approve=auto_approve)


def query_by_organization(
    organization_name: str,
    date_start: str = None,
    date_end: str = None,
    state: str = None,
    auto_approve: bool = False,
) -> QueryResult:
    """Query pits by organization"""
    query_filter = QueryFilter(
        organization_name=organization_name,
        date_start=date_start,
        date_end=date_end,
        state=state,
    )

    engine = QueryEngine()
    return engine.query_pits(query_filter, auto_approve=auto_approve)


def query_by_username(
    username: str,
    date_start: str = None,
    date_end: str = None,
    state: str = None,
    auto_approve: bool = False,
) -> QueryResult:
    """Query pits by username"""
    query_filter = QueryFilter(
        username=username, date_start=date_start, date_end=date_end, state=state
    )

    engine = QueryEngine()
    return engine.query_pits(query_filter, auto_approve=auto_approve)


def query_by_location(
    country: str = None,
    state: str = None,
    elevation_min: float = None,
    elevation_max: float = None,
    aspect: str = None,
    date_start: str = None,
    date_end: str = None,
    auto_approve: bool = False,
) -> QueryResult:
    """Query pits by location parameters"""
    query_filter = QueryFilter(
        country=country,
        state=state,
        elevation_min=elevation_min,
        elevation_max=elevation_max,
        aspect=aspect,
        date_start=date_start,
        date_end=date_end,
    )

    engine = QueryEngine()
    return engine.query_pits(query_filter, auto_approve=auto_approve)
