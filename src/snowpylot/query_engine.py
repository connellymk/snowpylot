"""
Query Engine for SnowPilot.org CAAML Data

This module provides tools for downloading and querying CAAML snow pit data
from snowpilot.org with flexible filtering capabilities.

The query engine automatically handles snowpilot.org's exclusive end date behavior
by applying a +1 day offset to all end dates, ensuring user-specified date ranges
work as expected (e.g., querying from 2023-01-01 to 2023-01-01 returns data for
that entire day).

Supported API Filter Fields:
- pit_name: Filter by pit name
- state: Filter by state code (e.g., 'MT', 'CO', 'WY')
- date_start/date_end: Filter by date range (YYYY-MM-DD format)
- username: Filter by username
- organization_name: Filter by organization name
- per_page: Number of results per page (max 100)
"""

import logging
import os
import re
import tarfile
import time
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from glob import glob
from typing import Any, Dict, List, Optional, Union

import requests

# Load environment variables from .env file if it exists
try:
    from dotenv import load_dotenv

    load_dotenv()  # This will load .env file automatically
except ImportError:
    # python-dotenv not installed, continue without it
    pass

from .caaml_parser import caaml_parser
from .snow_pit import SnowPit

# Configuration constants

# File and path settings
DEFAULT_PITS_PATH = "data/snowpits"

# Request and rate limiting settings
DEFAULT_REQUEST_DELAY = 15  # seconds between requests to prevent rate limiting
DEFAULT_MAX_RETRIES = 3  # default maximum retry attempts for requests

# Data settings
RESULTS_PER_PAGE = 100  # default number of results per page (max allowed by API: 100)

# URL endpoints
SNOWPILOT_BASE_URL = "https://snowpilot.org"
SNOWPILOT_LOGIN_PATH = "/user/login"
SNOWPILOT_CAAML_QUERY_PATH = "/avscience-query-caaml.xml?"
SNOWPILOT_DATA_URL = "https://snowpilot.org/sites/default/files/tmp/"

# Default date range settings
DEFAULT_DATE_RANGE_DAYS = 7  # default date range when dates not provided
MAX_DATE_RANGE_DAYS = 730  # warning threshold for very large date ranges (2 years)

# Approval and warning thresholds
DEFAULT_APPROVAL_THRESHOLD = 100  # number of pits above which approval is required
LARGE_DOWNLOAD_WARNING_THRESHOLD = 1000  # threshold for showing large download warning

# Retry delay multipliers
RETRY_DELAY_MULTIPLIER_AUTH = 2  # multiplier for auth retry delays
RETRY_DELAY_MULTIPLIER_403 = 3  # multiplier for 403 error retry delays

# Supported state codes and names
SUPPORTED_STATES = {
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
      Note: The query engine automatically adds +1 day to end_date to handle the API's
      exclusive end date behavior, so user-specified ranges work as expected.
    - username: Filter by username
    - organization_name: Filter by organization name
    - per_page: Number of results per page (max 100)
    - max_retries: Maximum retry attempts for failed requests
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
    max_retries: int = DEFAULT_MAX_RETRIES  # Maximum retry attempts for failed requests


@dataclass
class DryRunResult:
    """Data class for dry run information"""

    query_filter: Optional[QueryFilter] = None
    total_pits: int = 0

    def __str__(self) -> str:
        """Return a formatted dry run string"""
        return (
            f"Dry Run Result:\n"
            f"  Date range: {self.query_filter.date_start} to {self.query_filter.date_end}\n"
            f"  State: {self.query_filter.state or 'Any'}\n"
            f"  Username: {self.query_filter.username or 'Any'}\n"
            f"  Organization: {self.query_filter.organization_name or 'Any'}\n"
            f"  Total pits: {self.total_pits}\n"
            f"  Format: CAAML"
        )


@dataclass
class QueryResult:
    """Data class for query results"""

    snow_pits: List[SnowPit] = field(default_factory=list)
    total_count: int = 0
    query_filter: Optional[QueryFilter] = None
    download_info: Dict[str, Any] = field(default_factory=dict)
    dry_run_result: Optional[DryRunResult] = None
    status: str = "success"  # "success", "failed", "no_data"
    error_message: Optional[str] = None


class QueryBuilder:
    """Builds query parameters for snowpilot.org CAAML API"""

    def __init__(self):
        self.supported_states = SUPPORTED_STATES

    def build_caaml_query(self, query_filter: QueryFilter) -> str:
        """
        Build query string for CAAML endpoint with all required form parameters

        Automatically applies +1 day offset to end_date to handle snowpilot.org API's
        exclusive end date behavior (start <= date < end).
        """
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

        # Date parameters with automatic +1 day offset for end_date
        # This handles the API's exclusive end date behavior (start <= date < end)
        # The +1 day offset is ALWAYS applied when end_date is provided (no fallback)
        start_date = query_filter.date_start or ""
        end_date = query_filter.date_end or ""

        # Apply +1 day offset to end_date if it's provided
        # This ensures user-specified date ranges work as expected
        if end_date:
            end_date_obj = datetime.strptime(end_date, "%Y-%m-%d")
            # Add 1 day to make the range inclusive for the user's intended end date
            adjusted_end_date = end_date_obj + timedelta(days=1)
            end_date = adjusted_end_date.strftime("%Y-%m-%d")

        params.append(f"OBS_DATE_MIN={start_date}")
        params.append(f"OBS_DATE_MAX={end_date}")

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
        self.site_url = SNOWPILOT_BASE_URL
        self.login_url = self.site_url + SNOWPILOT_LOGIN_PATH
        self.caaml_query_url = self.site_url + SNOWPILOT_CAAML_QUERY_PATH
        self.data_url = SNOWPILOT_DATA_URL
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

    def _sleep_for_retry(
        self, attempt: int, max_retries: int, delay_multiplier: float, retry_type: str
    ):
        """
        Handle retry sleep and logging

        Args:
            attempt: Current attempt number (0-based)
            max_retries: Maximum number of retries
            delay_multiplier: Multiplier for the base delay
            retry_type: Description of what is being retried for logging
        """
        if attempt < max_retries - 1:
            logger.info(
                f"Retrying {retry_type}... (attempt {attempt + 1}/{max_retries})"
            )
            time.sleep(self.request_delay * delay_multiplier)

    def _get_credentials(self) -> tuple[Optional[str], Optional[str]]:
        """Get credentials from environment variables"""
        user = os.environ.get("SNOWPILOT_USER")
        password = os.environ.get("SNOWPILOT_PASSWORD")
        return user, password

    def _validate_credentials(
        self, user: Optional[str], password: Optional[str]
    ) -> bool:
        """Validate that credentials are present"""
        if not user or not password:
            logger.error(
                "SNOWPILOT_USER and SNOWPILOT_PASSWORD environment variables required"
            )
            return False
        return True

    def _create_auth_payload(self, user: str, password: str) -> dict:
        """Create authentication payload"""
        return {
            "name": user,
            "pass": password,
            "form_id": "user_login",
            "op": "Log in",
        }

    def authenticate(self) -> bool:
        """Authenticate with snowpilot.org with proper CSRF token handling"""
        user, password = self._get_credentials()

        if not self._validate_credentials(user, password):
            return False

        # Add a small delay before authentication to avoid rate limiting
        time.sleep(3)

        try:
            # Add realistic browser headers
            headers = {
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.5",
                "Accept-Encoding": "gzip, deflate, br",
                "Connection": "keep-alive",
                "Upgrade-Insecure-Requests": "1",
                "Referer": "https://snowpilot.org/",
            }

            # First, get the login page to extract CSRF tokens
            get_response = self.session.get(self.login_url, headers=headers)
            if get_response.status_code != 200:
                logger.error(f"Could not access login page: {get_response.status_code}")
                return False

            # Extract form_build_id from the login page
            form_build_id = self._extract_form_build_id(get_response.text)

            # Build payload with CSRF token
            payload = self._create_auth_payload(user, password)
            if form_build_id:
                payload["form_build_id"] = form_build_id
                logger.debug(f"Added form_build_id: {form_build_id}")

            # Add POST-specific headers
            post_headers = headers.copy()
            post_headers.update(
                {
                    "Content-Type": "application/x-www-form-urlencoded",
                    "Origin": "https://snowpilot.org",
                    "Referer": self.login_url,
                }
            )

            # Wait a bit more before POST
            time.sleep(2)

            response = self.session.post(
                self.login_url, data=payload, headers=post_headers
            )

            # Check for various success indicators
            if response.status_code == 200:
                response_text_lower = response.text.lower()

                # Check for explicit login failure messages first
                if (
                    "unrecognized username or password" in response_text_lower
                    or "invalid login" in response_text_lower
                    or "incorrect username" in response_text_lower
                    or "incorrect password" in response_text_lower
                    or "login failed" in response_text_lower
                ):
                    self.authenticated = False
                    logger.error("Authentication failed: Invalid username or password")
                    return False

                # Check if we're actually logged in
                if (
                    "logout" in response_text_lower
                    or "profile" in response_text_lower
                    or "user account" in response_text_lower
                    or "my account" in response_text_lower
                    or "dashboard" in response_text_lower
                    or response.url != self.login_url
                ):
                    self.authenticated = True
                    logger.info("Successfully authenticated with snowpilot.org")
                else:
                    self.authenticated = False
                    # Check if login form is still present (indicates failed login)
                    if (
                        'name="name"' in response.text
                        and 'name="pass"' in response.text
                    ):
                        logger.error(
                            "Authentication failed: Login form still present after POST"
                        )
                    else:
                        logger.error(
                            "Login POST returned 200 but no success indicators found"
                        )
            elif response.status_code in [301, 302]:
                # Check redirect location
                location = response.headers.get("Location", "")
                if "user" in location and "login" not in location:
                    self.authenticated = True
                    logger.info(
                        "Successfully authenticated with snowpilot.org (redirected)"
                    )
                else:
                    self.authenticated = False
                    logger.error(f"Login redirect to unexpected location: {location}")
            else:
                self.authenticated = False
                logger.error(
                    f"Authentication failed with status {response.status_code}"
                )
                if response.status_code == 403:
                    logger.warning(
                        "403 Forbidden - possible rate limiting or account block. Wait before retrying."
                    )
                logger.debug(f"Response content: {response.text[:500]}...")

            return self.authenticated

        except requests.RequestException as e:
            logger.error(f"Authentication error: {e}")
            return False

    def _extract_form_build_id(self, html_content: str) -> str:
        """Extract form_build_id from login page HTML"""
        try:
            # Look for form_build_id in hidden input field
            import re

            match = re.search(r'name="form_build_id"\s+value="([^"]+)"', html_content)
            if match:
                return match.group(1)
        except Exception as e:
            logger.debug(f"Could not extract form_build_id: {e}")
        return None

    def _create_authenticated_session(self) -> Optional[requests.Session]:
        """Create an authenticated session for making requests with CSRF token handling"""
        user, password = self._get_credentials()

        if not self._validate_credentials(user, password):
            return None

        # Add a small delay before authentication to avoid rate limiting
        time.sleep(3)

        session = requests.Session()
        try:
            # Add realistic browser headers
            headers = {
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.5",
                "Accept-Encoding": "gzip, deflate, br",
                "Connection": "keep-alive",
                "Upgrade-Insecure-Requests": "1",
                "Referer": "https://snowpilot.org/",
            }

            # First, get the login page to extract CSRF tokens
            get_response = session.get(self.login_url, headers=headers)
            if get_response.status_code != 200:
                logger.error(f"Could not access login page: {get_response.status_code}")
                return None

            # Extract form_build_id from the login page
            form_build_id = self._extract_form_build_id(get_response.text)

            # Build payload with CSRF token
            payload = self._create_auth_payload(user, password)
            if form_build_id:
                payload["form_build_id"] = form_build_id
                logger.debug(f"Added form_build_id: {form_build_id}")

            # Add POST-specific headers
            post_headers = headers.copy()
            post_headers.update(
                {
                    "Content-Type": "application/x-www-form-urlencoded",
                    "Origin": "https://snowpilot.org",
                    "Referer": self.login_url,
                }
            )

            # Wait a bit more before POST
            time.sleep(2)

            login_response = session.post(
                self.login_url, data=payload, headers=post_headers
            )

            # Check for success indicators
            if login_response.status_code == 200:
                response_text_lower = login_response.text.lower()

                # Check for explicit login failure messages first
                if (
                    "unrecognized username or password" in response_text_lower
                    or "invalid login" in response_text_lower
                    or "incorrect username" in response_text_lower
                    or "incorrect password" in response_text_lower
                    or "login failed" in response_text_lower
                ):
                    logger.error("Authentication failed: Invalid username or password")
                    return None

                # Verify login was successful
                if (
                    "logout" in response_text_lower
                    or "profile" in response_text_lower
                    or "user account" in response_text_lower
                    or "my account" in response_text_lower
                    or "dashboard" in response_text_lower
                    or login_response.url != self.login_url
                ):
                    return session
                else:
                    # Check if login form is still present (indicates failed login)
                    if (
                        'name="name"' in login_response.text
                        and 'name="pass"' in login_response.text
                    ):
                        logger.error(
                            "Authentication failed: Login form still present after POST"
                        )
                    else:
                        logger.error(
                            "Login POST returned 200 but no success indicators found"
                        )
                    return None
            elif login_response.status_code in [301, 302]:
                # Check redirect location
                location = login_response.headers.get("Location", "")
                if "user" in location and "login" not in location:
                    return session
                else:
                    logger.error(f"Login redirect to unexpected location: {location}")
                    return None
            else:
                logger.error(f"Login failed with status {login_response.status_code}")
                if login_response.status_code == 403:
                    logger.warning(
                        "403 Forbidden - possible rate limiting or account block"
                    )
                logger.debug(f"Response content: {login_response.text[:500]}...")
                return None
        except requests.RequestException as e:
            logger.error(f"Authentication error: {e}")
            return None

    def _make_caaml_request(
        self, query_string: str, max_retries: int = DEFAULT_MAX_RETRIES
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
                # Use the existing authenticated session if available and authenticated
                # Otherwise create a new one
                if self.authenticated and self.session:
                    session_to_use = self.session
                    logger.debug("Reusing existing authenticated session")
                else:
                    session_to_use = self._create_authenticated_session()
                    if not session_to_use:
                        self._sleep_for_retry(
                            attempt,
                            max_retries,
                            RETRY_DELAY_MULTIPLIER_AUTH,
                            "authentication",
                        )
                        if attempt < max_retries - 1:
                            continue
                        return None, None
                    logger.debug("Created new authenticated session")

                # Make the request using the session
                logger.info(f"Requesting CAAML data with query: {query_string}")
                self._enforce_rate_limit()
                query_response = session_to_use.get(self.caaml_query_url + query_string)

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
                    try:
                        match = re.search(r'filename="([^"]+)"', content_disposition)
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
                        file_response = session_to_use.get(file_url)

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
                                # Mark as not authenticated so we'll create a new session on retry
                                self.authenticated = False
                                self._sleep_for_retry(
                                    attempt,
                                    max_retries,
                                    RETRY_DELAY_MULTIPLIER_403,
                                    "after 403 error",
                                )
                                if attempt < max_retries - 1:
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
                        # Mark as not authenticated so we'll create a new session on retry
                        self.authenticated = False
                        self._sleep_for_retry(
                            attempt,
                            max_retries,
                            RETRY_DELAY_MULTIPLIER_403,
                            "after 403 error",
                        )
                        if attempt < max_retries - 1:
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
                # Mark as not authenticated so we'll create a new session on retry
                self.authenticated = False
                self._sleep_for_retry(
                    attempt,
                    max_retries,
                    RETRY_DELAY_MULTIPLIER_AUTH,
                    "after request exception",
                )
                if attempt < max_retries - 1:
                    continue
                return None, None

        # If we get here, all retries failed
        logger.error(f"Failed to make CAAML request after {max_retries} attempts")
        return None, None

    def download_caaml_data(
        self, query_string: str, max_retries: int = DEFAULT_MAX_RETRIES
    ) -> Optional[bytes]:
        """Download CAAML data from snowpilot.org"""
        data, filename = self._make_caaml_request(query_string, max_retries)
        return data


class QueryEngine:
    """Main query engine for snowpilot.org CAAML data"""

    def __init__(self, pits_path: str = DEFAULT_PITS_PATH):
        self.pits_path = pits_path
        self.session = SnowPilotSession()
        self.query_builder = QueryBuilder()
        os.makedirs(self.pits_path, exist_ok=True)

    def _create_state_filter(
        self, query_filter: QueryFilter, state: str
    ) -> QueryFilter:
        """
        Create a new QueryFilter for a specific state based on an existing filter

        Args:
            query_filter: Original query filter
            state: State code to use in the new filter

        Returns:
            New QueryFilter with the specified state
        """
        return QueryFilter(
            pit_name=query_filter.pit_name,
            date_start=query_filter.date_start,
            date_end=query_filter.date_end,
            state=state,
            username=query_filter.username,
            organization_name=query_filter.organization_name,
            per_page=query_filter.per_page,
            max_retries=query_filter.max_retries,
        )

    def _get_user_approval(
        self,
        total_pits: int,
        approval_threshold: int,
        prompt_message: str,
        cancellation_reason: str,
        display_info: Optional[str] = None,
    ) -> bool:
        """
        Get user approval for downloading pits

        Args:
            total_pits: Total number of pits to download
            approval_threshold: Threshold above which approval is required
            prompt_message: Message to show when prompting for approval
            cancellation_reason: Reason to log if user cancels
            display_info: Optional additional info to display before prompt

        Returns:
            True if user approves, False if user cancels
        """
        if total_pits <= approval_threshold:
            return True

        # Display information
        if display_info:
            print(f"\n{display_info}")

        print(f"\nThis query will download {total_pits} pits.")

        if total_pits > LARGE_DOWNLOAD_WARNING_THRESHOLD:
            print(
                "⚠️  WARNING: This is a large download that may take significant time and bandwidth."
            )

        response = input(f"\n{prompt_message} (y/N): ").lower().strip()

        if response not in ["y", "yes"]:
            logger.info(cancellation_reason)
            return False

        return True

    def dry_run(self, query_filter: QueryFilter) -> DryRunResult:
        """
        Perform a dry run to see how many pits would be downloaded

        Args:
            query_filter: Filter parameters for the query

        Returns:
            DryRunResult containing pit count information
        """
        logger.info(f"Performing dry run with filter: {query_filter}")

        # Validate and set default date range if not provided
        query_filter = self._validate_and_set_dates(query_filter)

        # For dry run, we'll make a minimal request just to get the count
        # without actually downloading the full data
        query_string = self.query_builder.build_caaml_query(query_filter)

        # Make a simple request to check if data exists and get approximate count
        # by checking the response headers without downloading the full file
        try:
            session = self.session._create_authenticated_session()
            if not session:
                logger.warning("Could not authenticate for dry run")
                return DryRunResult(query_filter=query_filter, total_pits=0)

            with session as s:
                response = s.head(self.session.caaml_query_url + query_string)

                # If we get a content-disposition header, data exists
                if response.headers.get("Content-Disposition"):
                    # For dry run, return a conservative estimate
                    # In a real implementation, you might parse the filename or make a small request
                    logger.info(
                        "Dry run: Data available (count estimation not implemented)"
                    )
                    estimated_count = 1  # Conservative estimate - data exists
                else:
                    estimated_count = 0

        except Exception as e:
            logger.warning(f"Dry run failed, assuming data exists: {e}")
            estimated_count = 1  # Conservative fallback

        return DryRunResult(
            query_filter=query_filter,
            total_pits=estimated_count,
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
            query_filter.date_start = (
                datetime.now() - timedelta(days=DEFAULT_DATE_RANGE_DAYS)
            ).strftime("%Y-%m-%d")
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
        if (end_date - start_date).days > MAX_DATE_RANGE_DAYS:
            logger.warning(
                f"Date range is very large ({(end_date - start_date).days} days). This may result in a very large download."
            )

        return query_filter

    def query_pits(
        self,
        query_filter: QueryFilter,
        auto_approve: bool = False,
        approval_threshold: int = DEFAULT_APPROVAL_THRESHOLD,
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

        # Get dry run first (only if approval might be needed)
        dry_run_result = None
        if not auto_approve:
            dry_run_result = self.dry_run(query_filter)

        # Check if approval is needed
        if not auto_approve and dry_run_result:
            if not self._get_user_approval(
                dry_run_result.total_pits,
                approval_threshold,
                "Do you want to proceed with the download?",
                "Download cancelled by user",
                str(dry_run_result),
            ):
                result = QueryResult(
                    query_filter=query_filter, dry_run_result=dry_run_result
                )
                result.download_info["status"] = "cancelled"
                result.download_info["reason"] = "User cancelled download"
                return result
            elif dry_run_result.total_pits <= approval_threshold:
                print(f"Dry run: Will download {dry_run_result.total_pits} pits")

        # Execute the CAAML query
        result = self._query_caaml(query_filter)

        # Add dry run info to result
        result.dry_run_result = dry_run_result
        return result

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
            # Skip pagination check for short date ranges (single day queries) to avoid duplicate calls
            date_range_days = 1  # Default assumption
            try:
                if query_filter.date_start and query_filter.date_end:
                    start_date = datetime.strptime(query_filter.date_start, "%Y-%m-%d")
                    end_date = datetime.strptime(query_filter.date_end, "%Y-%m-%d")
                    date_range_days = (end_date - start_date).days
            except:
                pass  # Use default if parsing fails

            if len(extracted_files) == query_filter.per_page and date_range_days > 1:
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
        approval_threshold: int = DEFAULT_APPROVAL_THRESHOLD,
    ) -> QueryResult:
        """
        Download snow pit data for any query filter

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
                state="MT"
            )
            result = engine.download_results(query_filter)

            # Multi-state query
            query_filter = QueryFilter(
                date_start="2023-01-01",
                date_end="2023-01-31",
                states=["MT", "CO", "WY"]
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
        approval_threshold: int = DEFAULT_APPROVAL_THRESHOLD,
    ) -> QueryResult:
        """
        Download results for multiple states

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

        # Get dry run counts for all states combined
        total_pits = 0
        for state in states:
            state_filter = self._create_state_filter(query_filter, state)
            dry_run = self.dry_run(state_filter)
            total_pits += dry_run.total_pits

        # Check if approval is needed for the combined total
        if not auto_approve:
            display_info = (
                f"Multi-state download summary:\n"
                f"  States: {', '.join(states)}\n"
                f"  Date range: {query_filter.date_start} to {query_filter.date_end}\n"
                f"  Total pits: {total_pits}"
            )

            if not self._get_user_approval(
                total_pits,
                approval_threshold,
                f"Do you want to proceed with downloading {total_pits} pits from {len(states)} states?",
                "Download cancelled by user",
                display_info,
            ):
                result = QueryResult(query_filter=query_filter)
                result.download_info["status"] = "cancelled"
                result.download_info["reason"] = "User cancelled multi-state download"
                return result

        # Download data for each state
        all_pits = []
        successful_states = []
        failed_states = []

        for state in states:
            logger.info(f"Downloading data for state: {state}")

            state_filter = self._create_state_filter(query_filter, state)

            try:
                state_result = self.query_pits(state_filter, auto_approve=True)
                all_pits.extend(state_result.snow_pits)
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
        )

        result.download_info = {
            "multi_state": True,
            "total_states": len(states),
            "successful_states": len(successful_states),
            "failed_states": len(failed_states),
            "states_processed": successful_states,
            "states_failed": failed_states,
            "total_pits": len(all_pits),
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

        return result
