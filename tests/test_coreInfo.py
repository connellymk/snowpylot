import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from snowpylot.caaml_parser import caaml_parser
from snowpylot.core_info import CoreInfo, Location, User, WeatherConditions


@pytest.fixture
def test_pit():
    """Fixture to load the test snowpit file"""
    return caaml_parser("snowpits/test/snowpylot-test-26-Feb-caaml.xml")


def test_core_info_structure(test_pit):
    """Test that CoreInfo object is properly structured"""
    core_info = test_pit.coreInfo
    assert isinstance(core_info, CoreInfo)
    assert isinstance(core_info.user, User)
    assert isinstance(core_info.location, Location)
    assert isinstance(core_info.weatherConditions, WeatherConditions)


def test_basic_core_info(test_pit):
    """Test basic core info fields"""
    core_info = test_pit.coreInfo
    assert core_info.pitID == "73109"
    assert core_info.pitName == "snowpylot-test"
    assert core_info.date == "2025-02-26"
    assert core_info.comment == "Core Info Comment"
    # assert core_info.caamlVersion == "{http://caaml.org/Schemas/SnowProfileIACS/v6.0.3}"


def test_user_info(test_pit):
    """Test user information"""
    user = test_pit.coreInfo.user
    assert user.username == "katisthebatis"
    assert user.userID == "SnowPilot-User-15812"
    assert user.professional is False
    assert user.operationID is None
    assert user.operationName is None


def test_location_info(test_pit):
    """Test location information"""
    location = test_pit.coreInfo.location
    assert location.latitude == 45.828056
    assert location.longitude == -110.932875
    assert location.elevation == [2598.0, "m"]
    assert location.aspect == "NE"
    assert location.slopeAngle == ["30", "deg"]
    assert location.country == "US"
    assert location.region == "MT"
    assert location.pitNearAvalanche is True
    assert location.pitNearAvalancheLocation == "crown"

    # def test_weather_conditions(test_pit):
    """Test weather conditions"""

    weather = test_pit.coreInfo.weatherConditions
    assert weather.skyCond == "SCT"
    assert weather.precipTI == "Nil"
    assert weather.airTempPres == [28.0, "degC"]
    assert weather.windSpeed == "C"
    assert weather.windDir == "SW"


def test_professional_user():
    """Test parsing of a professional user with operation info"""
    # This is a mock of what a professional user's XML might look like
    xml_content = """
    <caaml:srcRef>
        <caaml:Operation gml:id="SnowPilot-Operation-123">
            <caaml:name>Professional Org</caaml:name>
        </caaml:Operation>
        <caaml:ContactPerson gml:id="SnowPilot-User-456">
            <caaml:name>Pro Observer</caaml:name>
        </caaml:ContactPerson>
    </caaml:srcRef>
    """
    core_info = CoreInfo()
    core_info.parse_xml(xml_content)
    assert core_info.operation_name == "Professional Org"
    assert core_info.observer_name == "Pro Observer"


def test_missing_optional_fields(test_pit):
    """Test handling of missing optional fields"""
    core_info = test_pit.coreInfo

    # These fields should be None or have default values if not present
    assert core_info.user.operationID is None
    assert core_info.user.operationName is None
    assert core_info.user.professional is False  # default value


def test_string_representation(test_pit):
    """Test string representation of CoreInfo objects"""
    core_info = test_pit.coreInfo
    str_repr = str(core_info)

    # Check that important fields are included in string representation
    assert "PitID: 73109" in str_repr
    assert "PitName: snowpylot-test" in str_repr
    assert "Date: 2025-02-26" in str_repr
    assert "Comment: Core Info Comment" in str_repr

    # Check nested object string representations
    user_str = str(core_info.user)
    assert "Username: katisthebatis" in user_str
    assert "Professional: False" in user_str

    location_str = str(core_info.location)
    assert "Latitude: 45.828056" in location_str
    assert "Longitude: -110.932875" in location_str

    # weather_str = str(core_info.weatherConditions)
    # assert "skyCond: SCT" in weather_str
    # assert "windDir: SW" in weather_str


if __name__ == "__main__":
    pytest.main([__file__])
