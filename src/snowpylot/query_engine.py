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
import time
from datetime import datetime, timedelta
from glob import glob
from typing import Dict, List, Optional, Union, Any
from dataclasses import dataclass, field

import requests

from .caaml_parser import caaml_parser
from .snow_pit import SnowPit

# Configuration constants
DEFAULT_PITS_PATH = "data/snowpits"
DEFAULT_REQUEST_DELAY = 2  # seconds between requests to prevent rate limiting

# Create basic logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class QueryFilter:
    """Data class for query filter parameters"""

    pit_id: Optional[str] = None
    pit_name: Optional[str] = None
    date_start: Optional[Union[str, datetime, Any]] = (
        None  # Format: YYYY-MM-DD or datetime-like object
    )
    date_end: Optional[Union[str, datetime, Any]] = (
        None  # Format: YYYY-MM-DD or datetime-like object
    )
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
    per_page: int = 100  # Default to 100 to match working implementation


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
        per_page = min(query_filter.per_page, 100)
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

    def download_caaml_data(self, query_string: str) -> Optional[bytes]:
        """Download CAAML data from snowpilot.org (single request with all pits)"""
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
                login_response = s.post(self.login_url, data=payload)
                if login_response.status_code != 200:
                    logger.error(
                        f"Login failed with status {login_response.status_code}"
                    )
                    return None

                logger.info(f"Requesting CAAML data with query: {query_string}")
                self._enforce_rate_limit()
                query_response = s.get(self.caaml_query_url + query_string)

                # Debug logging
                logger.debug(f"Query response status: {query_response.status_code}")
                logger.debug(f"Query response headers: {dict(query_response.headers)}")

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
                    try:
                        filename = content_disposition[22:-1].replace("_caaml", "")
                        if not filename or filename == ".tar.gz":
                            logger.error(
                                f"Invalid filename extracted from Content-Disposition: '{content_disposition}'"
                            )
                            return None

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
                            if file_response.status_code == 403:
                                logger.error(
                                    "403 Forbidden - possible rate limiting or authentication issue"
                                )
                                logger.error(
                                    "Consider adding delays between requests or checking credentials"
                                )
                            return None
                    except Exception as e:
                        logger.error(
                            f"Error parsing Content-Disposition header '{content_disposition}': {e}"
                        )
                        return None
                else:
                    logger.warning(
                        f"CAAML download failed with status {query_response.status_code}"
                    )
                    if query_response.status_code == 403:
                        logger.error(
                            "403 Forbidden - possible rate limiting or authentication issue"
                        )
                        logger.error(
                            "Try reducing query frequency or checking credentials"
                        )
                    elif query_response.status_code == 500:
                        logger.error(
                            "Server error (500) - this may indicate an issue with the query parameters or server"
                        )
                    elif content_disposition is None:
                        logger.error(
                            "No Content-Disposition header found - query may have returned no results"
                        )
                    return None

        except requests.RequestException as e:
            logger.error(f"CAAML download error: {e}")
            return None

    def preview_query(self, query_string: str) -> int:
        """
        Preview a query to get the estimated count of pits
        Downloads and counts the actual CAAML files

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
                login_response = s.post(self.login_url, data=payload)
                if login_response.status_code != 200:
                    logger.error(
                        f"Preview login failed with status {login_response.status_code}"
                    )
                    return 0

                logger.info(f"Previewing query: {query_string}")

                # Try to get the CAAML data to see if it's available
                self._enforce_rate_limit()
                response = s.get(self.caaml_query_url + query_string)

                # Debug logging
                logger.debug(f"Preview response status: {response.status_code}")
                logger.debug(f"Preview response headers: {dict(response.headers)}")

                # Check if we got a successful response
                content_disposition = response.headers.get("Content-Disposition", None)
                if content_disposition is not None and response.status_code == 200:
                    # Extract filename from Content-Disposition header
                    try:
                        filename = content_disposition[22:-1].replace("_caaml", "")
                        if not filename or filename == ".tar.gz":
                            logger.error(
                                f"Invalid filename extracted from Content-Disposition: '{content_disposition}'"
                            )
                            return 0

                        file_url = self.data_url + filename

                        # Download and extract the file to count pits
                        file_response = s.get(file_url)
                        if file_response.status_code == 200:
                            # Create a temporary file to extract and count
                            import tempfile

                            with tempfile.NamedTemporaryFile(
                                suffix=".tar.gz", delete=False
                            ) as temp_file:
                                temp_file.write(file_response.content)
                                temp_file_path = temp_file.name

                            try:
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
                                import shutil

                                shutil.rmtree(extract_path, ignore_errors=True)
                                os.remove(temp_file_path)

                                logger.info(f"Preview found exactly {pit_count} pits")
                                return pit_count

                            except Exception as e:
                                logger.error(f"Error during preview extraction: {e}")
                                # Clean up on error
                                try:
                                    shutil.rmtree(extract_path, ignore_errors=True)
                                    os.remove(temp_file_path)
                                except:
                                    pass
                                return 0
                        else:
                            logger.warning(
                                f"Preview file download failed with status {file_response.status_code}"
                            )
                            if file_response.status_code == 403:
                                logger.error(
                                    "403 Forbidden - possible rate limiting or authentication issue"
                                )
                                logger.error(
                                    "Consider adding delays between requests or checking credentials"
                                )
                            return 0
                    except Exception as e:
                        logger.error(
                            f"Error parsing Content-Disposition header '{content_disposition}': {e}"
                        )
                        return 0
                else:
                    if response.status_code == 403:
                        logger.error(
                            "403 Forbidden - possible rate limiting or authentication issue"
                        )
                        logger.error(
                            "Try reducing query frequency or checking credentials"
                        )
                    elif content_disposition is None:
                        logger.info(
                            f"Preview shows no data available - no Content-Disposition header (status: {response.status_code})"
                        )
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
                    per_page=500,  # Try larger batch
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
