import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from snowpylot.caaml_parser import caaml_parser
from snowpylot.whumpf_data import WhumpfData


@pytest.fixture
def test_pit():
    """Fixture to load the test snowpit file"""
    return caaml_parser("snowpits/test/snowpits-25670-wumph-caaml.xml")


def test_whumpf_data_structure(test_pit):
    """Test that WhumpfData object is properly structured"""
    whumpf_data = test_pit.whumpfData
    assert isinstance(whumpf_data, WhumpfData)


def test_whumpf_data_values(test_pit):
    """Test whumpf data values"""
    whumpf_data = test_pit.whumpfData

    # Test boolean values
    assert whumpf_data.whumpfCracking == "true"
    assert whumpf_data.whumpfNoCracking == "false"
    assert whumpf_data.crackingNoWhumpf == "false"
    assert whumpf_data.whumpfNearPit == "true"
    assert whumpf_data.whumpfDepthWeakLayer == "true"
    assert whumpf_data.whumpfTriggeredRemoteAva == "false"

    # Test empty/optional value
    assert whumpf_data.whumpfSize is None or whumpf_data.whumpfSize == ""


def test_string_representation(test_pit):
    """Test string representation of WhumpfData object"""
    whumpf_data = test_pit.whumpfData
    str_repr = str(whumpf_data)

    # Check that all fields are included in string representation
    assert "whumpfCracking: true" in str_repr
    assert "whumpfNoCracking: false" in str_repr
    assert "crackingNoWhumpf: false" in str_repr
    assert "whumpfNearPit: true" in str_repr
    assert "whumpfDepthWeakLayer: true" in str_repr
    assert "whumpfTriggeredRemoteAva: false" in str_repr
    assert "whumpfSize: " in str_repr


def test_missing_whumpf_data():
    """Test handling of missing whumpf data"""
    # Load the non-whumpf test file
    pit = caaml_parser("snowpits/test/snowpylot-test-26-Feb-caaml.xml")

    # Check that whumpf data is None when not present in XML
    assert pit.whumpfData is None


if __name__ == "__main__":
    pytest.main([__file__])
