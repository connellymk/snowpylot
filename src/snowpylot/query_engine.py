"""
Query Engine for SnowPilot.org Data

This module provides tools for downloading and querying CAAML snow pit data
from snowpilot.org with flexible filtering capabilities.
"""

import json
import logging
import os
import shutil
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
from glob import glob
from typing import Dict, List, Optional, Union, Any
from dataclasses import dataclass, field

import pandas as pd
import requests

from .caaml_parser import caaml_parser
from .snow_pit import SnowPit

# Configuration constants (since config.py is missing)
DEFAULT_PITS_PATH = "data/snowpits"
DEFAULT_STATES_DATA_PATH = "data/states_data.json"

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
    per_page: int = 1000


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
            f"  Organization: {self.query_filter.organization_name or 'Any'}\n"
            f"  Elevation: {self.query_filter.elevation_min or 'Any'} - {self.query_filter.elevation_max or 'Any'}m\n"
            f"  Format: {self.preview_info.get('format', 'CAAML')}"
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
    """Builds query parameters for snowpilot.org API"""

    def __init__(self):
        self.supported_states = {
            "MT": {"id": "27", "name": "Montana"},
            "CO": {"id": "8", "name": "Colorado"},
            "WY": {"id": "51", "name": "Wyoming"},
            "UT": {"id": "45", "name": "Utah"},
            "ID": {"id": "16", "name": "Idaho"},
            "WA": {"id": "48", "name": "Washington"},
            "OR": {"id": "41", "name": "Oregon"},
            "CA": {"id": "6", "name": "California"},
            "AK": {"id": "2", "name": "Alaska"},
            "NH": {"id": "33", "name": "New Hampshire"},
            "VT": {"id": "46", "name": "Vermont"},
            "ME": {"id": "23", "name": "Maine"},
            "NY": {"id": "36", "name": "New York"},
        }

    def build_xml_query(self, query_filter: QueryFilter) -> str:
        """Build query string for XML endpoint"""
        params = []

        if query_filter.state and query_filter.state in self.supported_states:
            state_id = self.supported_states[query_filter.state]["id"]
            params.append(f"STATE[{state_id}]={state_id}")

        if query_filter.date_start:
            params.append(f"OBS_DATE_MIN={query_filter.date_start}")

        if query_filter.date_end:
            params.append(f"OBS_DATE_MAX={query_filter.date_end}")

        params.append(f"per_page={query_filter.per_page}")

        return "&".join(params)

    def build_caaml_query(self, query_filter: QueryFilter) -> str:
        """Build query string for CAAML endpoint"""
        params = []

        if query_filter.state:
            params.append(f"STATE={query_filter.state}")

        if query_filter.date_start:
            params.append(f"OBS_DATE_MIN={query_filter.date_start}")

        if query_filter.date_end:
            params.append(f"OBS_DATE_MAX={query_filter.date_end}")

        params.append(f"per_page={query_filter.per_page}")

        return "&".join(params)


class SnowPilotSession:
    """Manages authentication and session with snowpilot.org"""

    def __init__(self):
        self.session = requests.Session()
        self.authenticated = False
        self.site_url = "https://snowpilot.org"
        self.login_url = self.site_url + "/user/login"
        self.xml_query_url = self.site_url + "/snowpilot-query-feed.xml?"
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

    def download_xml_data(self, query_string: str) -> Optional[str]:
        """Download XML data from snowpilot.org"""
        if not self.authenticated:
            if not self.authenticate():
                return None

        try:
            response = self.session.post(
                self.xml_query_url + query_string, data=query_string
            )

            if response.status_code == 200 and '<?xml version="1.0"' in response.text:
                logger.info("XML download successful")
                return response.text
            else:
                logger.warning(
                    f"XML download failed with status {response.status_code}"
                )
                return None

        except requests.RequestException as e:
            logger.error(f"XML download error: {e}")
            return None

    def download_caaml_data(self, query_string: str) -> Optional[str]:
        """Download CAAML data from snowpilot.org"""
        if not self.authenticated:
            if not self.authenticate():
                return None

        try:
            response = self.session.post(self.caaml_query_url + query_string)

            content_disposition = response.headers.get("Content-Disposition")
            if content_disposition and response.status_code == 200:
                filename = content_disposition[22:-1].replace("_caaml", "")
                file_url = self.data_url + filename

                file_response = self.session.get(file_url)
                if file_response.status_code == 200:
                    logger.info(f"CAAML download successful: {filename}")
                    return file_response.content

            logger.warning(f"CAAML download failed with status {response.status_code}")
            return None

        except requests.RequestException as e:
            logger.error(f"CAAML download error: {e}")
            return None

    def preview_query(self, query_string: str, format_type: str = "xml") -> int:
        """
        Preview a query to get the estimated count of pits without downloading all data

        Args:
            query_string: The query string to preview
            format_type: 'xml' or 'caaml' format type

        Returns:
            Estimated number of pits that would be downloaded
        """
        if not self.authenticated:
            if not self.authenticate():
                return 0

        try:
            # Use XML endpoint for preview as it's lighter
            preview_query = (
                query_string + "&per_page=1"
            )  # Limit to 1 result for preview
            response = self.session.post(
                self.xml_query_url + preview_query, data=preview_query
            )

            if response.status_code == 200 and '<?xml version="1.0"' in response.text:
                # Parse the XML to extract total count information
                try:
                    root = ET.fromstring(response.text)

                    # Count the number of pit entries in the response
                    # This is a rough estimate based on the first page
                    pit_entries = []
                    for elem in root.iter():
                        # Look for elements that indicate individual pits
                        if (
                            "snowpit" in elem.tag.lower()
                            or "observation" in elem.tag.lower()
                        ):
                            pit_entries.append(elem)

                    # If we got results with per_page=1, try to get more info
                    # by making another request with a higher limit to get better estimate
                    if pit_entries:
                        estimate_query = (
                            query_string + "&per_page=50"
                        )  # Get more for better estimate
                        estimate_response = self.session.post(
                            self.xml_query_url + estimate_query, data=estimate_query
                        )

                        if estimate_response.status_code == 200:
                            estimate_root = ET.fromstring(estimate_response.text)
                            estimate_count = 0

                            # Count actual pit entries in the larger sample
                            for elem in estimate_root.iter():
                                if "item" in elem.tag.lower():  # RSS-style items
                                    estimate_count += 1

                            logger.info(
                                f"Preview found approximately {estimate_count} pits"
                            )
                            return estimate_count

                    return len(pit_entries)

                except ET.ParseError as e:
                    logger.error(f"Error parsing preview XML: {e}")
                    return 0
            else:
                logger.warning(
                    f"Preview request failed with status {response.status_code}"
                )
                return 0

        except requests.RequestException as e:
            logger.error(f"Preview request error: {e}")
            return 0


class QueryEngine:
    """Main query engine for snowpilot.org data"""

    def __init__(self, pits_path: str = DEFAULT_PITS_PATH):
        self.pits_path = pits_path
        self.session = SnowPilotSession()
        self.query_builder = QueryBuilder()
        os.makedirs(self.pits_path, exist_ok=True)

    def preview_query(
        self, query_filter: QueryFilter, data_format: str = "caaml"
    ) -> QueryPreview:
        """
        Preview a query to see how many pits would be downloaded

        Args:
            query_filter: Filter parameters for the query
            data_format: 'xml' or 'caaml' format

        Returns:
            QueryPreview containing estimated count and filter info
        """
        logger.info(f"Previewing query with filter: {query_filter}")

        # Set default date range if not provided
        if not query_filter.date_start:
            query_filter.date_start = (datetime.now() - timedelta(days=7)).strftime(
                "%Y-%m-%d"
            )
        if not query_filter.date_end:
            query_filter.date_end = datetime.now().strftime("%Y-%m-%d")

        # Build query string for preview
        query_string = self.query_builder.build_xml_query(query_filter)

        # Get estimated count
        estimated_count = self.session.preview_query(query_string, data_format)

        # Create preview object
        preview = QueryPreview(
            estimated_count=estimated_count,
            query_filter=query_filter,
            preview_info={"format": data_format.upper(), "query_string": query_string},
        )

        return preview

    def query_pits(
        self,
        query_filter: QueryFilter,
        data_format: str = "caaml",
        auto_approve: bool = False,
        approval_threshold: int = 100,
    ) -> QueryResult:
        """
        Query snow pits from snowpilot.org

        Args:
            query_filter: Filter parameters for the query
            data_format: 'xml' or 'caaml' format
            auto_approve: If True, skip approval prompt
            approval_threshold: Number of pits above which approval is required

        Returns:
            QueryResult containing snow pit data
        """
        logger.info(f"Querying pits with filter: {query_filter}")

        # Set default date range if not provided
        if not query_filter.date_start:
            query_filter.date_start = (datetime.now() - timedelta(days=7)).strftime(
                "%Y-%m-%d"
            )
        if not query_filter.date_end:
            query_filter.date_end = datetime.now().strftime("%Y-%m-%d")

        # Get preview first
        preview = self.preview_query(query_filter, data_format)

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

        if data_format == "xml":
            result = self._query_xml(query_filter)
        elif data_format == "caaml":
            result = self._query_caaml(query_filter)
        else:
            raise ValueError("data_format must be 'xml' or 'caaml'")

        # Add preview info to result
        result.preview = preview
        return result

    def _query_xml(self, query_filter: QueryFilter) -> QueryResult:
        """Query XML data from snowpilot.org"""
        query_string = self.query_builder.build_xml_query(query_filter)
        xml_data = self.session.download_xml_data(query_string)

        result = QueryResult(query_filter=query_filter)

        if xml_data:
            # Save XML data to file
            filename = f"{query_filter.date_start}_{query_filter.date_end}_pits.xml"
            filepath = os.path.join(self.pits_path, filename)

            try:
                tree = ET.ElementTree(ET.fromstring(xml_data))
                tree.write(filepath)
                result.download_info["saved_file"] = filepath
                result.download_info["format"] = "xml"

                # Parse XML and extract pit data
                result.snow_pits = self._parse_xml_pits(xml_data, query_filter)
                result.total_count = len(result.snow_pits)

            except ET.ParseError as e:
                logger.error(f"XML parsing error: {e}")

        return result

    def _query_caaml(self, query_filter: QueryFilter) -> QueryResult:
        """Query CAAML data from snowpilot.org"""
        query_string = self.query_builder.build_caaml_query(query_filter)
        caaml_data = self.session.download_caaml_data(query_string)

        result = QueryResult(query_filter=query_filter)

        if caaml_data:
            # Save CAAML data to file
            filename = f"{query_filter.date_start}_{query_filter.date_end}_pits.tar.gz"
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
            shutil.unpack_archive(archive_path, extract_path)

            # Find all CAAML XML files
            caaml_files = []
            for root, dirs, files in os.walk(extract_path):
                for file in files:
                    if file.endswith("caaml.xml"):
                        caaml_files.append(os.path.join(root, file))

            # Clean up
            shutil.rmtree(extract_path, ignore_errors=True)
            os.remove(archive_path)

            return caaml_files

        except Exception as e:
            logger.error(f"Error extracting CAAML files: {e}")
            return []

    def _parse_xml_pits(
        self, xml_data: str, query_filter: QueryFilter
    ) -> List[SnowPit]:
        """Parse XML data and extract snow pits"""
        # This is a simplified parser - in practice, you'd need to handle
        # the XML structure specific to snowpilot.org bulk XML format
        pits = []

        try:
            root = ET.fromstring(xml_data)

            # Extract individual pit elements (this would depend on the actual XML structure)
            # For now, this is a placeholder implementation

            logger.info(f"Parsed {len(pits)} pits from XML data")

        except ET.ParseError as e:
            logger.error(f"Error parsing XML data: {e}")

        return pits

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
    start_date: str, end_date: str, state: str = None, data_format: str = "caaml"
) -> QueryPreview:
    """Preview pits by date range"""
    query_filter = QueryFilter(date_start=start_date, date_end=end_date, state=state)

    engine = QueryEngine()
    return engine.preview_query(query_filter, data_format)


def query_by_date_range(
    start_date: str, end_date: str, state: str = None, auto_approve: bool = False
) -> QueryResult:
    """Query pits by date range"""
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
    auto_approve: bool = False,
) -> QueryResult:
    """Query pits by organization"""
    query_filter = QueryFilter(
        organization_name=organization_name, date_start=date_start, date_end=date_end
    )

    engine = QueryEngine()
    return engine.query_pits(query_filter, auto_approve=auto_approve)


def query_by_location(
    country: str = None,
    state: str = None,
    elevation_min: float = None,
    elevation_max: float = None,
    aspect: str = None,
    auto_approve: bool = False,
) -> QueryResult:
    """Query pits by location parameters"""
    query_filter = QueryFilter(
        country=country,
        state=state,
        elevation_min=elevation_min,
        elevation_max=elevation_max,
        aspect=aspect,
    )

    engine = QueryEngine()
    return engine.query_pits(query_filter, auto_approve=auto_approve)
