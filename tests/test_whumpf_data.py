import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest

from snowpylot.caaml_parser import caaml_parser
from snowpylot.whumpf_data import WhumpfData


@pytest.fixture
def test_pit():
    """Fixture to load the test snowpit file"""
    return caaml_parser("demos/snowpits/test/snowpits-25670-wumph-caaml.xml")


def test_whumpf_data_structure(test_pit):
    """Test that WhumpfData object is properly structured"""
    whumpf_data = test_pit.whumpf_data
    assert isinstance(whumpf_data, WhumpfData)


def test_whumpf_data_values(test_pit):
    """Test whumpf data values"""
    whumpf_data = test_pit.whumpf_data

    # Test boolean values
    assert whumpf_data.whumpf_cracking == "true"
    assert whumpf_data.whumpf_no_cracking == "false"
    assert whumpf_data.cracking_no_whumpf == "false"
    assert whumpf_data.whumpf_near_pit == "true"
    assert whumpf_data.whumpf_depth_weak_layer == "true"
    assert whumpf_data.whumpf_triggered_remote_ava == "false"

    # Test empty/optional value
    assert whumpf_data.whumpf_size is None or whumpf_data.whumpf_size == ""


def test_string_representation(test_pit):
    """Test string representation of WhumpfData object"""
    whumpf_data = test_pit.whumpf_data
    str_repr = str(whumpf_data)

    # Check that all fields are included in string representation
    assert "whumpf_cracking: true" in str_repr
    assert "whumpf_no_cracking: false" in str_repr
    assert "cracking_no_whumpf: false" in str_repr
    assert "whumpf_near_pit: true" in str_repr
    assert "whumpf_depth_weak_layer: true" in str_repr
    assert "whumpf_triggered_remote_ava: false" in str_repr
    assert "whumpf_size: " in str_repr


def test_missing_whumpf_data():
    """Test handling of missing whumpf data"""
    # Load the non-whumpf test file
    pit = caaml_parser("demos/snowpits/test/snowpylot-test-26-Feb-caaml.xml")

    # Check that whumpf data is None when not present in XML
    assert pit.whumpf_data is None


if __name__ == "__main__":
    pytest.main([__file__])
