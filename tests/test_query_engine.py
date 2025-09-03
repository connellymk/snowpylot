#!/usr/bin/env python3
"""
Test suite for the SnowPylot Query Engine

This test suite verifies that the query engine works correctly with the existing
codebase and handles various scenarios properly.
"""

import unittest
import tempfile
import os
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
import sys
import shutil

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from snowpylot.query_engine import (
    QueryEngine,
    QueryFilter,
    QueryResult,
    QueryBuilder,
    SnowPilotSession,
    DryRunResult,
    ChunkInfo,
    ProgressTracker,
)
from snowpylot.snow_pit import SnowPit
from snowpylot.caaml_parser import caaml_parser


class TestQueryFilter(unittest.TestCase):
    """Test QueryFilter functionality"""

    def test_query_filter_creation(self):
        """Test creating QueryFilter with various parameters"""
        query_filter = QueryFilter(
            pit_id="13720",
            pit_name="Test Pit",
            date_start="2024-01-01",
            date_end="2024-01-31",
            state="MT",
            username="testuser",
            elevation_min=2000,
            elevation_max=3000,
        )

        self.assertEqual(query_filter.pit_id, "13720")
        self.assertEqual(query_filter.pit_name, "Test Pit")
        self.assertEqual(query_filter.date_start, "2024-01-01")
        self.assertEqual(query_filter.date_end, "2024-01-31")
        self.assertEqual(query_filter.state, "MT")
        self.assertEqual(query_filter.username, "testuser")
        self.assertEqual(query_filter.elevation_min, 2000)
        self.assertEqual(query_filter.elevation_max, 3000)

    def test_query_filter_defaults(self):
        """Test QueryFilter default values"""
        query_filter = QueryFilter()

        self.assertIsNone(query_filter.pit_id)
        self.assertIsNone(query_filter.pit_name)
        self.assertIsNone(query_filter.date_start)
        self.assertIsNone(query_filter.date_end)
        self.assertEqual(query_filter.per_page, 100)


class TestQueryBuilder(unittest.TestCase):
    """Test QueryBuilder functionality"""

    def setUp(self):
        self.query_builder = QueryBuilder()

    def test_supported_states(self):
        """Test that supported states are correctly configured"""
        self.assertIn("MT", self.query_builder.supported_states)
        self.assertIn("CO", self.query_builder.supported_states)
        self.assertEqual(self.query_builder.supported_states["MT"]["id"], "27")
        self.assertEqual(self.query_builder.supported_states["CO"]["id"], "8")

    def test_build_xml_query(self):
        """Test building XML query string"""
        query_filter = QueryFilter(
            state="MT", date_start="2024-01-01", date_end="2024-01-31", per_page=500
        )

        query_string = self.query_builder.build_xml_query(query_filter)

        self.assertIn("STATE[27]=27", query_string)
        self.assertIn("OBS_DATE_MIN=2024-01-01", query_string)
        self.assertIn("OBS_DATE_MAX=2024-01-31", query_string)
        self.assertIn("per_page=500", query_string)

    def test_build_caaml_query(self):
        """Test building CAAML query string"""
        query_filter = QueryFilter(
            state="CO", date_start="2024-01-01", date_end="2024-01-31"
        )

        query_string = self.query_builder.build_caaml_query(query_filter)

        self.assertIn("STATE=CO", query_string)
        self.assertIn("OBS_DATE_MIN=2024-01-01", query_string)
        self.assertIn("OBS_DATE_MAX=2024-01-31", query_string)
        self.assertIn("per_page=100", query_string)

    def test_unsupported_state(self):
        """Test handling of unsupported state"""
        query_filter = QueryFilter(state="XX")
        query_string = self.query_builder.build_xml_query(query_filter)

        self.assertNotIn("STATE", query_string)


class TestSnowPilotSession(unittest.TestCase):
    """Test SnowPilotSession functionality"""

    def setUp(self):
        self.session = SnowPilotSession()

    def test_session_initialization(self):
        """Test session initialization"""
        self.assertFalse(self.session.authenticated)
        self.assertEqual(self.session.site_url, "https://snowpilot.org")
        self.assertIsNotNone(self.session.session)

    @patch.dict(
        os.environ, {"SNOWPILOT_USER": "testuser", "SNOWPILOT_PASSWORD": "testpass"}
    )
    @patch("requests.Session.post")
    def test_authenticate_success(self, mock_post):
        """Test successful authentication"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response

        result = self.session.authenticate()

        self.assertTrue(result)
        self.assertTrue(self.session.authenticated)
        mock_post.assert_called_once()

    @patch.dict(
        os.environ, {"SNOWPILOT_USER": "testuser", "SNOWPILOT_PASSWORD": "testpass"}
    )
    @patch("requests.Session.post")
    def test_authenticate_failure(self, mock_post):
        """Test failed authentication"""
        mock_response = Mock()
        mock_response.status_code = 401
        mock_post.return_value = mock_response

        result = self.session.authenticate()

        self.assertFalse(result)
        self.assertFalse(self.session.authenticated)

    def test_authenticate_missing_credentials(self):
        """Test authentication with missing credentials"""
        with patch.dict(os.environ, {}, clear=True):
            result = self.session.authenticate()

            self.assertFalse(result)
            self.assertFalse(self.session.authenticated)


class TestQueryEngine(unittest.TestCase):
    """Test QueryEngine functionality"""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.engine = QueryEngine(pits_path=self.temp_dir)

    def tearDown(self):
        # Clean up temporary directory
        import shutil

        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_engine_initialization(self):
        """Test QueryEngine initialization"""
        self.assertEqual(self.engine.pits_path, self.temp_dir)
        self.assertIsNotNone(self.engine.session)
        self.assertIsNotNone(self.engine.query_builder)
        self.assertTrue(os.path.exists(self.temp_dir))

    def test_query_filter_date_defaults(self):
        """Test that default dates are set when not provided"""
        query_filter = QueryFilter(state="MT")

        # Mock the session to avoid actual API calls
        with patch.object(self.engine, "_query_caaml") as mock_query:
            mock_result = QueryResult()
            mock_query.return_value = mock_result

            result = self.engine.query_pits(query_filter)

            # Check that dates were set
            self.assertIsNotNone(query_filter.date_start)
            self.assertIsNotNone(query_filter.date_end)

    def test_invalid_data_format(self):
        """Test invalid data format raises error"""
        query_filter = QueryFilter(state="MT")

        with self.assertRaises(ValueError):
            self.engine.query_pits(query_filter, data_format="invalid")

    def test_matches_filter_pit_id(self):
        """Test filter matching by pit ID"""
        # Create a mock SnowPit
        pit = SnowPit()
        pit.core_info.pit_id = "13720"

        query_filter = QueryFilter(pit_id="13720")
        self.assertTrue(self.engine._matches_filter(pit, query_filter))

        query_filter = QueryFilter(pit_id="99999")
        self.assertFalse(self.engine._matches_filter(pit, query_filter))

    def test_matches_filter_state(self):
        """Test filter matching by state"""
        pit = SnowPit()
        pit.core_info.location.region = "MT"

        query_filter = QueryFilter(state="MT")
        self.assertTrue(self.engine._matches_filter(pit, query_filter))

        query_filter = QueryFilter(state="CO")
        self.assertFalse(self.engine._matches_filter(pit, query_filter))

    def test_matches_filter_elevation(self):
        """Test filter matching by elevation"""
        pit = SnowPit()
        pit.core_info.location.elevation = (2500.0, "m")

        query_filter = QueryFilter(elevation_min=2000, elevation_max=3000)
        self.assertTrue(self.engine._matches_filter(pit, query_filter))

        query_filter = QueryFilter(elevation_min=3000, elevation_max=4000)
        self.assertFalse(self.engine._matches_filter(pit, query_filter))

    def test_matches_filter_username(self):
        """Test filter matching by username"""
        pit = SnowPit()
        pit.core_info.user.username = "testuser"

        query_filter = QueryFilter(username="testuser")
        self.assertTrue(self.engine._matches_filter(pit, query_filter))

        query_filter = QueryFilter(username="test")  # Partial match
        self.assertTrue(self.engine._matches_filter(pit, query_filter))

        query_filter = QueryFilter(username="otheruser")
        self.assertFalse(self.engine._matches_filter(pit, query_filter))


class TestLocalSearch(unittest.TestCase):
    """Test local search functionality"""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.engine = QueryEngine(pits_path=self.temp_dir)

    def tearDown(self):
        import shutil

        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_search_local_pits_no_files(self):
        """Test local search with no files"""
        query_filter = QueryFilter(state="MT")
        result = self.engine.search_local_pits(query_filter)

        self.assertEqual(result.total_count, 0)
        self.assertEqual(len(result.snow_pits), 0)
        self.assertEqual(result.download_info["files_searched"], 0)

    @patch("snowpylot.query_engine.caaml_parser")
    @patch("glob.glob")
    def test_search_local_pits_with_files(self, mock_glob, mock_parser):
        """Test local search with files"""
        # Mock file discovery
        mock_files = [
            os.path.join(self.temp_dir, "pit1-caaml.xml"),
            os.path.join(self.temp_dir, "pit2-caaml.xml"),
        ]
        mock_glob.return_value = mock_files

        # Mock parser
        mock_pit = SnowPit()
        mock_pit.core_info.location.region = "MT"
        mock_parser.return_value = mock_pit

        query_filter = QueryFilter(state="MT")
        result = self.engine.search_local_pits(query_filter)

        self.assertEqual(result.total_count, 2)
        self.assertEqual(len(result.snow_pits), 2)
        self.assertEqual(result.download_info["files_searched"], 2)


class TestIntegrationWithExistingCode(unittest.TestCase):
    """Test integration with existing SnowPylot code"""

    def test_query_result_with_existing_parser(self):
        """Test that QueryResult works with existing CAAML parser"""
        # Test with actual test file if available
        test_file = os.path.join(
            os.path.dirname(__file__),
            "..",
            "demos",
            "snowpits",
            "test",
            "snowpits-13720-caaml.xml",
        )

        if os.path.exists(test_file):
            # Parse the test file
            pit = caaml_parser(test_file)

            # Create a QueryResult with the parsed pit
            result = QueryResult()
            result.snow_pits = [pit]
            result.total_count = 1

            # Verify the structure
            self.assertEqual(result.total_count, 1)
            self.assertEqual(len(result.snow_pits), 1)

            # Verify the pit data
            parsed_pit = result.snow_pits[0]
            self.assertIsInstance(parsed_pit, SnowPit)
            self.assertEqual(parsed_pit.core_info.pit_id, "13720")
            self.assertEqual(parsed_pit.core_info.location.region, "MT")
            self.assertEqual(parsed_pit.core_info.user.username, "benschmidt5")
        else:
            self.skipTest("Test CAAML file not found")


class TestQueryEngineAPI(unittest.TestCase):
    """Test main QueryEngine API with different QueryFilter combinations"""

    def setUp(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
        self.engine = QueryEngine(pits_path=self.temp_dir)

    def tearDown(self):
        """Clean up test fixtures"""
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    @patch("snowpylot.query_engine.SnowPilotSession")
    def test_date_range_query(self, mock_session_class):
        """Test date range query using QueryFilter"""
        mock_session = Mock()
        mock_session.authenticate.return_value = True
        mock_session.download_caaml_data.return_value = None
        mock_session.estimate_pit_count.return_value = 5
        mock_session_class.return_value = mock_session

        query_filter = QueryFilter(
            date_start="2024-01-01", date_end="2024-01-31", state="MT"
        )

        # Test dry run
        dry_run_result = self.engine.dry_run(query_filter)
        self.assertIsInstance(dry_run_result, DryRunResult)
        self.assertEqual(dry_run_result.query_filter.date_start, "2024-01-01")
        self.assertEqual(dry_run_result.query_filter.date_end, "2024-01-31")
        self.assertEqual(dry_run_result.query_filter.state, "MT")

    @patch("snowpylot.query_engine.SnowPilotSession")
    def test_organization_query(self, mock_session_class):
        """Test organization query using QueryFilter"""
        mock_session = Mock()
        mock_session.authenticate.return_value = True
        mock_session.download_caaml_data.return_value = None
        mock_session.estimate_pit_count.return_value = 3
        mock_session_class.return_value = mock_session

        query_filter = QueryFilter(
            organization_name="Test Organization",
            date_start="2024-01-01",
            date_end="2024-01-31",
            state="MT",
        )

        # Test dry run
        dry_run_result = self.engine.dry_run(query_filter)
        self.assertIsInstance(dry_run_result, DryRunResult)
        self.assertEqual(
            dry_run_result.query_filter.organization_name, "Test Organization"
        )
        self.assertEqual(dry_run_result.query_filter.date_start, "2024-01-01")
        self.assertEqual(dry_run_result.query_filter.state, "MT")

    @patch("snowpylot.query_engine.SnowPilotSession")
    def test_username_query(self, mock_session_class):
        """Test username query using QueryFilter"""
        mock_session = Mock()
        mock_session.authenticate.return_value = True
        mock_session.download_caaml_data.return_value = None
        mock_session.estimate_pit_count.return_value = 2
        mock_session_class.return_value = mock_session

        query_filter = QueryFilter(
            username="testuser",
            date_start="2024-01-01",
            date_end="2024-01-31",
            state="MT",
        )

        # Test dry run
        dry_run_result = self.engine.dry_run(query_filter)
        self.assertIsInstance(dry_run_result, DryRunResult)
        self.assertEqual(dry_run_result.query_filter.username, "testuser")
        self.assertEqual(dry_run_result.query_filter.date_start, "2024-01-01")
        self.assertEqual(dry_run_result.query_filter.state, "MT")

    @patch("snowpylot.query_engine.SnowPilotSession")
    def test_combined_filters_query(self, mock_session_class):
        """Test query with multiple combined filters"""
        mock_session = Mock()
        mock_session.authenticate.return_value = True
        mock_session.download_caaml_data.return_value = None
        mock_session.estimate_pit_count.return_value = 1
        mock_session_class.return_value = mock_session

        query_filter = QueryFilter(
            username="testuser",
            organization_name="Test Organization",
            date_start="2024-01-01",
            date_end="2024-01-31",
            state="MT",
            pit_name="Test Pit",
        )

        # Test dry run
        dry_run_result = self.engine.dry_run(query_filter)
        self.assertIsInstance(dry_run_result, DryRunResult)
        self.assertEqual(dry_run_result.query_filter.username, "testuser")
        self.assertEqual(
            dry_run_result.query_filter.organization_name, "Test Organization"
        )
        self.assertEqual(dry_run_result.query_filter.pit_name, "Test Pit")
        self.assertEqual(dry_run_result.query_filter.state, "MT")

    @patch("snowpylot.query_engine.SnowPilotSession")
    def test_chunked_query(self, mock_session_class):
        """Test chunked query using QueryFilter"""
        mock_session = Mock()
        mock_session.authenticate.return_value = True
        mock_session.download_caaml_data.return_value = None
        mock_session.estimate_pit_count.return_value = 10
        mock_session_class.return_value = mock_session

        query_filter = QueryFilter(
            date_start="2024-01-01",
            date_end="2024-01-31",
            state="MT",
            chunk=True,
            chunk_size_days=7,
        )

        # Test dry run
        dry_run_result = self.engine.dry_run(query_filter)
        self.assertIsInstance(dry_run_result, DryRunResult)
        self.assertTrue(dry_run_result.will_be_chunked)
        self.assertEqual(dry_run_result.chunk_size_days, 7)

    @patch("snowpylot.query_engine.SnowPilotSession")
    def test_download_results_single_state(self, mock_session_class):
        """Test download_results method with single state"""
        mock_session = Mock()
        mock_session.authenticate.return_value = True
        mock_session.download_caaml_data.return_value = None
        mock_session.estimate_pit_count.return_value = 5
        mock_session_class.return_value = mock_session

        query_filter = QueryFilter(
            date_start="2024-01-01", date_end="2024-01-31", state="MT"
        )

        # Test download_results (should delegate to query_pits)
        result = self.engine.download_results(query_filter, auto_approve=True)
        self.assertIsInstance(result, QueryResult)
        self.assertEqual(result.query_filter.state, "MT")

    @patch("snowpylot.query_engine.SnowPilotSession")
    def test_download_results_multi_state(self, mock_session_class):
        """Test download_results method with multiple states"""
        mock_session = Mock()
        mock_session.authenticate.return_value = True
        mock_session.download_caaml_data.return_value = None
        mock_session.estimate_pit_count.return_value = 3
        mock_session_class.return_value = mock_session

        query_filter = QueryFilter(
            date_start="2024-01-01",
            date_end="2024-01-31",
            states=["MT", "CO", "WY"],
            chunk=True,
            chunk_size_days=7,
        )

        # Test multi-state download
        result = self.engine.download_results(query_filter, auto_approve=True)
        self.assertIsInstance(result, QueryResult)
        self.assertEqual(result.query_filter.states, ["MT", "CO", "WY"])
        self.assertTrue(result.download_info.get("multi_state", False))
        self.assertEqual(result.download_info.get("total_states", 0), 3)


if __name__ == "__main__":
    # Run the tests
    unittest.main(verbosity=2)
