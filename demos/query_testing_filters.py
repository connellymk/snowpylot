#!/usr/bin/env python3
"""
Query Engine API Filter Testing

This script tests each of the filter fields that are supported by the Snow Pilot API
to demonstrate their functionality and help with development/debugging.

API Filter Fields (sent to snowpilot.org):
- pit_name: Filter by pit name
- state: Filter by state code (e.g., 'MT', 'CO', 'WY')
- date_start/date_end: Filter by date range (YYYY-MM-DD format)
- username: Filter by username
- organization_name: Filter by organization name
- per_page: Number of results per page (max 100)

Client-side Filter Fields (applied after download):
- pit_id: Filter by specific pit ID
- country: Filter by country
- elevation_min/max: Filter by elevation range
- aspect: Filter by aspect
"""

import os
import sys
from datetime import datetime, timedelta

sys.path.append("../src")

from snowpylot.query_engine import QueryEngine, QueryFilter

# Configuration
TEST_DATE_START = "2023-12-01"  # Use recent dates for testing
TEST_DATE_END = "2023-12-31"
TEST_STATE = "MT"  # Montana typically has good data
MAX_RESULTS_PER_TEST = 10  # Keep tests fast


def print_section(title):
    """Print a formatted section header"""
    print(f"\n{'=' * 60}")
    print(f"🔧 {title}")
    print("=" * 60)


def print_results(result, test_name, expected_behavior=None):
    """Print test results in a consistent format"""
    print(f"\n--- {test_name} Results ---")
    print(f"Total pits found: {result.total_count}")
    print(f"Was chunked: {result.was_chunked}")

    if expected_behavior:
        print(f"Expected behavior: {expected_behavior}")

    if result.snow_pits:
        print(f"Example pits (showing first 3):")
        for i, pit in enumerate(result.snow_pits[:3]):
            print(f"  {i + 1}. {pit.core_info.pit_id} - {pit.core_info.pit_name}")
            if pit.core_info.location:
                print(f"     Location: {pit.core_info.location.region}")
            if pit.core_info.user:
                print(f"     User: {pit.core_info.user.username}")
            if pit.core_info.date:
                print(f"     Date: {pit.core_info.date}")
    else:
        print("No pits found")


def test_environment():
    """Test environment setup and authentication"""
    print_section("Environment Setup")

    user = os.environ.get("SNOWPILOT_USER")
    password = os.environ.get("SNOWPILOT_PASSWORD")

    if user and password:
        print("✅ Environment variables are set!")
        print(f"   SNOWPILOT_USER: {user}")
        print(f"   SNOWPILOT_PASSWORD: {'*' * len(password)}")
    else:
        print("❌ Environment variables not set!")
        print("   Please set SNOWPILOT_USER and SNOWPILOT_PASSWORD")
        sys.exit(1)

    print("\n--- Testing Authentication ---")
    engine = QueryEngine()
    auth_success = engine.session.authenticate()

    if auth_success:
        print("✅ Authentication successful!")
        return engine
    else:
        print("❌ Authentication failed!")
        print("   Check your credentials and try again")
        sys.exit(1)


def test_date_range_filter(engine):
    """Test date_start and date_end filters"""
    print_section("Date Range Filter Testing")

    # Test 1: Basic date range
    print("\n🔍 Test 1: Basic Date Range")
    query_filter = QueryFilter(
        date_start=TEST_DATE_START,
        date_end=TEST_DATE_END,
        state=TEST_STATE,
        per_page=MAX_RESULTS_PER_TEST,
        chunk=False,
    )

    try:
        result = engine.query_pits(query_filter, auto_approve=True)
        print_results(
            result,
            "Basic Date Range",
            "Should return pits within the specified date range",
        )
    except Exception as e:
        print(f"❌ Error: {e}")

    # Test 2: Single day
    print("\n🔍 Test 2: Single Day")
    single_day = "2023-12-15"
    query_filter = QueryFilter(
        date_start=single_day,
        date_end=single_day,
        state=TEST_STATE,
        per_page=MAX_RESULTS_PER_TEST,
        chunk=False,
    )

    try:
        result = engine.query_pits(query_filter, auto_approve=True)
        print_results(result, "Single Day", "Should return pits from exactly one day")
    except Exception as e:
        print(f"❌ Error: {e}")


def test_state_filter(engine):
    """Test state filter"""
    print_section("State Filter Testing")

    # Test 1: No state defined - should return pits from all states
    print("\n🔍 Testing No State (All States)")
    query_filter = QueryFilter(
        date_start=TEST_DATE_START,
        date_end=TEST_DATE_END,
        state=None,  # No state filter
        per_page=MAX_RESULTS_PER_TEST,
        chunk=False,
    )

    try:
        result = engine.query_pits(query_filter, auto_approve=True)
        print_results(
            result,
            "No State Filter",
            "Should return pits from all states, not default to MT",
        )

        # Verify we got pits from multiple states
        if result.snow_pits:
            states_found = set()
            for pit in result.snow_pits:
                if pit.core_info.location and pit.core_info.location.region:
                    states_found.add(pit.core_info.location.region)

            print(f"✅ States found in results: {sorted(states_found)}")
            if len(states_found) > 1:
                print(f"✅ Multiple states confirmed - not defaulting to MT")
            elif len(states_found) == 1 and "MT" in states_found:
                print(
                    f"⚠️  Only MT found - this might be expected if MT has the most data in this date range"
                )
            else:
                print(f"✅ Single state found: {states_found}")

    except Exception as e:
        print(f"❌ Error: {e}")

    # Test 2: Test different specific states
    test_states = ["MT", "CO", "WY", "UT"]

    for state in test_states:
        print(f"\n🔍 Testing State: {state}")
        query_filter = QueryFilter(
            date_start=TEST_DATE_START,
            date_end=TEST_DATE_END,
            state=state,
            per_page=MAX_RESULTS_PER_TEST,
            chunk=False,
        )

        try:
            result = engine.query_pits(query_filter, auto_approve=True)
            print_results(
                result,
                f"State Filter ({state})",
                f"Should return pits from {state} only",
            )
        except Exception as e:
            print(f"❌ Error: {e}")


def test_username_filter(engine):
    """Test username filter"""
    print_section("Username Filter Testing")

    # Test 1: Get some pits first to find real usernames
    print("\n🔍 Finding real usernames for testing...")
    query_filter = QueryFilter(
        date_start=TEST_DATE_START,
        date_end=TEST_DATE_END,
        state=TEST_STATE,
        per_page=20,
        chunk=False,
    )

    try:
        result = engine.query_pits(query_filter, auto_approve=True)

        # Extract unique usernames
        usernames = set()
        for pit in result.snow_pits:
            if pit.core_info.user and pit.core_info.user.username:
                usernames.add(pit.core_info.user.username)

        print(f"Found {len(usernames)} unique usernames")

        # Test with the first few usernames
        test_usernames = list(usernames)[:3]

        for username in test_usernames:
            print(f"\n🔍 Testing Username: {username}")
            query_filter = QueryFilter(
                date_start=TEST_DATE_START,
                date_end=TEST_DATE_END,
                state=TEST_STATE,
                username=username,
                per_page=MAX_RESULTS_PER_TEST,
                chunk=False,
            )

            result = engine.query_pits(query_filter, auto_approve=True)
            print_results(
                result,
                f"Username Filter ({username})",
                f"Should return pits from user '{username}' only",
            )

    except Exception as e:
        print(f"❌ Error: {e}")


def test_organization_filter(engine):
    """Test organization_name filter"""
    print_section("Organization Filter Testing")

    # Test 1: Get some pits first to find real organizations
    print("\n🔍 Finding real organizations for testing...")
    query_filter = QueryFilter(
        date_start=TEST_DATE_START,
        date_end=TEST_DATE_END,
        state=TEST_STATE,
        per_page=20,
        chunk=False,
    )

    try:
        result = engine.query_pits(query_filter, auto_approve=True)

        # Extract unique organizations
        organizations = set()
        for pit in result.snow_pits:
            if pit.core_info.user and pit.core_info.user.operation_name:
                organizations.add(pit.core_info.user.operation_name)

        print(f"Found {len(organizations)} unique organizations")

        # Test with the first few organizations
        test_orgs = list(organizations)[:3]

        for org in test_orgs:
            print(f"\n🔍 Testing Organization: {org}")
            query_filter = QueryFilter(
                date_start=TEST_DATE_START,
                date_end=TEST_DATE_END,
                state=TEST_STATE,
                organization_name=org,
                per_page=MAX_RESULTS_PER_TEST,
                chunk=False,
            )

            result = engine.query_pits(query_filter, auto_approve=True)
            print_results(
                result,
                f"Organization Filter ({org})",
                f"Should return pits from organization '{org}' only",
            )

    except Exception as e:
        print(f"❌ Error: {e}")


def test_pit_name_filter(engine):
    """Test pit_name filter"""
    print_section("Pit Name Filter Testing")

    # Test 1: Get some pits first to find real pit names
    print("\n🔍 Finding real pit names for testing...")
    query_filter = QueryFilter(
        date_start=TEST_DATE_START,
        date_end=TEST_DATE_END,
        state=TEST_STATE,
        per_page=20,
        chunk=False,
    )

    try:
        result = engine.query_pits(query_filter, auto_approve=True)

        # Extract pit names
        pit_names = []
        for pit in result.snow_pits:
            if pit.core_info.pit_name:
                pit_names.append(pit.core_info.pit_name)

        print(f"Found {len(pit_names)} pit names")

        # Test with the first few pit names
        test_names = pit_names[:3]

        for pit_name in test_names:
            print(f"\n🔍 Testing Pit Name: {pit_name}")
            query_filter = QueryFilter(
                date_start=TEST_DATE_START,
                date_end=TEST_DATE_END,
                state=TEST_STATE,
                pit_name=pit_name,
                per_page=MAX_RESULTS_PER_TEST,
                chunk=False,
            )

            result = engine.query_pits(query_filter, auto_approve=True)
            print_results(
                result,
                f"Pit Name Filter ({pit_name})",
                f"Should return pits with name containing '{pit_name}'",
            )

    except Exception as e:
        print(f"❌ Error: {e}")


def test_per_page_filter(engine):
    """Test per_page filter"""
    print_section("Per Page Filter Testing")

    test_values = [1, 5, 10, 50, 100]

    for per_page in test_values:
        print(f"\n🔍 Testing per_page: {per_page}")
        query_filter = QueryFilter(
            date_start=TEST_DATE_START,
            date_end=TEST_DATE_END,
            state=TEST_STATE,
            per_page=per_page,
            chunk=False,
        )

        try:
            result = engine.query_pits(query_filter, auto_approve=True)
            print_results(
                result,
                f"Per Page ({per_page})",
                f"Should return at most {per_page} pits",
            )

            # Verify the per_page limit is respected
            if result.total_count > per_page:
                print(
                    f"⚠️  Warning: Got {result.total_count} pits, expected at most {per_page}"
                )
            else:
                print(
                    f"✅ Per page limit respected: {result.total_count} <= {per_page}"
                )

        except Exception as e:
            print(f"❌ Error: {e}")


def test_combined_filters(engine):
    """Test combining multiple filters"""
    print_section("Combined Filter Testing")

    print("\n🔍 Testing Combined Filters")
    query_filter = QueryFilter(
        date_start=TEST_DATE_START,
        date_end=TEST_DATE_END,
        state=TEST_STATE,
        per_page=5,
        chunk=False,
    )

    try:
        # First get some data to use for combined testing
        result = engine.query_pits(query_filter, auto_approve=True)

        if result.snow_pits:
            sample_pit = result.snow_pits[0]
            username = (
                sample_pit.core_info.user.username
                if sample_pit.core_info.user
                else None
            )

            if username:
                print(f"\n🔍 Testing Date + State + Username combination")
                combined_filter = QueryFilter(
                    date_start=TEST_DATE_START,
                    date_end=TEST_DATE_END,
                    state=TEST_STATE,
                    username=username,
                    per_page=MAX_RESULTS_PER_TEST,
                    chunk=False,
                )

                combined_result = engine.query_pits(combined_filter, auto_approve=True)
                print_results(
                    combined_result,
                    "Combined Filters",
                    f"Should return pits from {TEST_STATE} by user '{username}' in date range",
                )

    except Exception as e:
        print(f"❌ Error: {e}")


def test_client_side_filters(engine):
    """Test client-side filters (applied after download)"""
    print_section("Client-Side Filter Testing")

    print("📝 Note: These filters are applied after download, not sent to the API")

    # Test elevation filter
    print("\n🔍 Testing Elevation Filter (client-side)")
    query_filter = QueryFilter(
        date_start=TEST_DATE_START,
        date_end=TEST_DATE_END,
        state=TEST_STATE,
        elevation_min=2000,
        elevation_max=3000,
        per_page=MAX_RESULTS_PER_TEST,
        chunk=False,
    )

    try:
        result = engine.query_pits(query_filter, auto_approve=True)
        print_results(
            result,
            "Elevation Filter",
            "Should return pits between 2000-3000m elevation",
        )

        # Verify elevation filtering worked
        for pit in result.snow_pits[:3]:
            if pit.core_info.location and pit.core_info.location.elevation:
                elevation = pit.core_info.location.elevation[0]
                print(f"   Elevation: {elevation}m")

    except Exception as e:
        print(f"❌ Error: {e}")


def main():
    """Run all filter tests"""
    print("🚀 Snow Pilot API Filter Testing")
    print("=" * 60)
    print("This script tests each filter field supported by the Snow Pilot API")
    print("to demonstrate their functionality and help with development.")
    print(f"\nTest configuration:")
    print(f"  Date range: {TEST_DATE_START} to {TEST_DATE_END}")
    print(f"  Primary state: {TEST_STATE}")
    print(f"  Max results per test: {MAX_RESULTS_PER_TEST}")

    # Setup
    engine = test_environment()

    # API Filter Tests
    test_date_range_filter(engine)
    test_state_filter(engine)
    test_username_filter(engine)
    test_organization_filter(engine)
    test_pit_name_filter(engine)
    test_per_page_filter(engine)
    test_combined_filters(engine)

    # Client-side Filter Tests
    test_client_side_filters(engine)

    # Summary
    print_section("Testing Complete")
    print("✅ All filter tests completed!")
    print("\n📊 Summary:")
    print("   - API filters are sent to snowpilot.org and applied server-side")
    print("   - Client-side filters are applied after download")
    print("   - Combine filters for more specific queries")
    print("   - Use smaller date ranges for faster testing")
    print("\n💡 Tips:")
    print("   - Montana (MT) typically has the most data")
    print("   - Recent dates (last 1-2 years) are most reliable")
    print("   - Use chunk=False for testing to avoid chunking overhead")
    print("   - Check result.total_count to verify filter effectiveness")


if __name__ == "__main__":
    main()
