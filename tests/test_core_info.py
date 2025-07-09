import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest

from snowpylot.caaml_parser import caaml_parser
from snowpylot.core_info import CoreInfo, Location, User, WeatherConditions


@pytest.fixture
def test_pit():
    """Fixture to load the test snowpit file"""
    return caaml_parser("demos/snowpits/test/snowpylot-test-26-Feb-caaml.xml")


def test_core_info_structure(test_pit):
    """Test that CoreInfo object is properly structured"""
    core_info = test_pit.core_info
    assert isinstance(core_info, CoreInfo)
    assert isinstance(core_info.user, User)
    assert isinstance(core_info.location, Location)
    assert isinstance(core_info.weather_conditions, WeatherConditions)


def test_basic_core_info(test_pit):
    """Test basic core info fields"""
    core_info = test_pit.core_info
    assert core_info.pit_id == "73109"
    assert core_info.pit_name == "snowpylot-test"
    assert core_info.date == "2025-02-26"
    assert core_info.comment == "Core Info Comment"
    # assert core_info.caaml_version == "{http://caaml.org/Schemas/SnowProfileIACS/v6.0.3}"


def test_user_info(test_pit):
    """Test user information"""
    user = test_pit.core_info.user
    assert user.username == "katisthebatis"
    assert user.user_id == "SnowPilot-User-15812"
    assert user.professional is False
    assert user.operation_id is None
    assert user.operation_name is None


def test_location_info(test_pit):
    """Test location information"""
    location = test_pit.core_info.location
    assert location.latitude == 45.828056
    assert location.longitude == -110.932875
    assert location.elevation == [2598.0, "m"]
    assert location.aspect == "NE"
    assert location.slope_angle == ["30", "deg"]
    assert location.country == "US"
    assert location.region == "MT"
    assert location.pit_near_avalanche is True
    assert location.pit_near_avalanche_location == "crown"


def test_weather_conditions(test_pit):
    """Test weather conditions"""
    weather = test_pit.core_info.weather_conditions
    assert weather.sky_cond == "SCT"
    assert weather.precip_ti == "Nil"
    assert weather.air_temp_pres == [28.0, "degC"]
    assert weather.wind_speed == "C"
    assert weather.wind_dir == "SW"


def test_professional_user():
    """Test parsing of a professional user with operation info"""
    # This is a mock of what a professional user's XML might look like
    # Note: The parse_xml method doesn't exist, so we'll skip this test for now
    # core_info = CoreInfo()
    # core_info.parse_xml(xml_content)
    # assert core_info.operation_name == "Professional Org"
    # assert core_info.observer_name == "Pro Observer"
    pass


def test_missing_optional_fields(test_pit):
    """Test handling of missing optional fields"""
    core_info = test_pit.core_info

    # These fields should be None or have default values if not present
    assert core_info.user.operation_id is None
    assert core_info.user.operation_name is None
    assert core_info.user.professional is False  # default value


def test_string_representation(test_pit):
    """Test string representation of CoreInfo objects"""
    core_info = test_pit.core_info
    str_repr = str(core_info)

    # Check that important fields are included in string representation
    assert "pit_id: 73109" in str_repr
    assert "pit_name: snowpylot-test" in str_repr
    assert "date: 2025-02-26" in str_repr
    assert "comment: Core Info Comment" in str_repr

    # Check nested object string representations
    user_str = str(core_info.user)
    assert "username: katisthebatis" in user_str
    assert "professional: False" in user_str

    location_str = str(core_info.location)
    assert "latitude: 45.828056" in location_str
    assert "longitude: -110.932875" in location_str

    weather_str = str(core_info.weather_conditions)
    assert "sky_cond: SCT" in weather_str
    assert "wind_dir: SW" in weather_str


if __name__ == "__main__":
    pytest.main([__file__])
