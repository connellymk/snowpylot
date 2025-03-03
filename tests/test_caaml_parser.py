import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


import pytest
from datetime import datetime
from caaml_parser import caaml_parser
from snowPit import SnowPit
from layer import Layer, Grain


@pytest.fixture
def test_pit():
    """Fixture to load the test snowpit file"""
    return caaml_parser("snowpits/test/snowpylot-test-26-Feb-caaml.xml")


def test_basic_pit_info(test_pit):
    """Test basic snowpit information parsing"""
    assert isinstance(test_pit, SnowPit)
    assert test_pit.caamlVersion == "{http://caaml.org/Schemas/SnowProfileIACS/v6.0.3}"
    assert test_pit.coreInfo.pitID == "73109"
    assert test_pit.coreInfo.date == "2025-02-26"
    assert test_pit.coreInfo.pitName == "snowpylot-test"
    assert test_pit.coreInfo.comment == "Core Info Comment"


def test_user_info(test_pit):
    """Test user information parsing"""
    assert test_pit.coreInfo.user.username == "katisthebatis"
    assert test_pit.coreInfo.user.userID == "SnowPilot-User-15812"
    assert test_pit.coreInfo.user.professional is False  # No operation info in test file


def test_location_info(test_pit):
    """Test location information parsing"""
    assert test_pit.coreInfo.location.latitude == 45.828056
    assert test_pit.coreInfo.location.longitude == -110.932875
    assert test_pit.coreInfo.location.elevation == ["2598", "m"]
    assert test_pit.coreInfo.location.aspect == "NE"
    assert test_pit.coreInfo.location.slopeAngle == ["30", "deg"]
    assert test_pit.coreInfo.location.country == "US"
    assert test_pit.coreInfo.location.region == "MT"
    assert test_pit.coreInfo.location.avalancheProximity is True
    assert test_pit.coreInfo.location.avalancheProximityLocation == "crown"


def test_snow_profile_basic(test_pit):
    """Test basic snow profile information"""
    assert test_pit.snowProfile.measurementDirection == "top down"
    assert test_pit.snowProfile.profileDepth == ["155", "cm"]
    assert test_pit.snowProfile.hS == ["155", "cm"]


def test_weather_conditions(test_pit):
    """Test weather conditions parsing"""
    weather = test_pit.snowProfile.weatherConditions
    assert weather.skyCond == "SCT"
    assert weather.precipTI == "Nil"
    assert weather.airTempPres == [28.0, "degC"]
    assert weather.windSpeed == "C"
    assert weather.windDir == "SW"


def test_surface_conditions(test_pit):
    """Test surface conditions parsing"""
    surface = test_pit.snowProfile.surfCond
    assert surface.windLoading == "previous"
    assert surface.penetrationFoot == [60.0, "cm"]
    assert surface.penetrationSki == [20.0, "cm"]


def test_layers(test_pit):
    """Test snow layers parsing"""
    layers = test_pit.snowProfile.layers
    assert len(layers) == 11  # Test file has 11 layers

    # Test first layer
    layer1 = layers[0]
    assert layer1.depthTop == ["0", "cm"]
    assert layer1.thickness == ["11", "cm"]
    assert layer1.hardness == "F"
    assert layer1.wetness == "D-M"
    assert isinstance(layer1.grainFormPrimary, Grain)
    assert layer1.grainFormPrimary.grainForm == "RG"
    assert layer1.grainFormSecondary.grainForm == "DF"
    assert layer1.grainFormPrimary.grainSizeAvg == [0.5, "mm"]
    assert layer1.comments == "layer 1 comment"

    # Test layer of concern (layer 7)
    layer7 = layers[6]
    assert layer7.layerOfConcern == "true"
    assert layer7.depthTop == ["66", "cm"]
    assert layer7.grainFormPrimary.grainForm == "SHxr"
    assert layer7.grainFormSecondary.grainForm == "FCxr"
    assert layer7.comments == "layer 7 comment"


def test_temperature_profile(test_pit):
    """Test temperature profile parsing"""
    temps = test_pit.snowProfile.tempProfile
    assert len(temps) == 16  # Test file has 16 temperature measurements

    # Test first temperature measurement
    assert temps[0].depth == ["0", "cm"]
    assert temps[0].snowTemp == [-2.2222222222222, "degC"]

    # Test last temperature measurement
    assert temps[-1].depth == ["145", "cm"]
    assert temps[-1].snowTemp == [-2.2222222222222, "degC"]


def test_stability_tests(test_pit):
    """Test stability tests parsing"""
    # Test ECTs
    assert len(test_pit.stabilityTests.ECT) == 2
    ect1 = test_pit.stabilityTests.ECT[0]
    assert ect1.depthTop == [11.0, "cm"]
    assert ect1.testScore == "ECTN4"
    assert ect1.propogation is False
    assert ect1.numTaps == "4"
    assert ect1.comment == "ECT 1 comment"

    # Test CTs
    assert len(test_pit.stabilityTests.CT) == 3
    ct1 = test_pit.stabilityTests.CT[0]
    assert ct1.depthTop == [11.0, "cm"]
    assert ct1.testScore == "13"
    assert ct1.shearQuality == "Q2"
    assert ct1.comment == "CT comment 1"

    # Test RBT
    assert len(test_pit.stabilityTests.RBT) == 1
    rbt = test_pit.stabilityTests.RBT[0]
    assert rbt.depthTop == [120.0, "cm"]
    assert rbt.testScore == "RB3"
    assert rbt.releaseType == "MB"
    assert rbt.shearQuality == "Q2"
    assert rbt.comment == "RBlock 1 comment"

    # Test PST
    assert len(test_pit.stabilityTests.PST) == 1
    pst = test_pit.stabilityTests.PST[0]
    assert pst.depthTop == [65.0, "cm"]
    assert pst.fractureProp == "Arr"
    assert pst.cutLength == "13.0"
    assert pst.columnLength == "100.0"
    assert pst.comment == "PST comment"


if __name__ == "__main__":
    pytest.main([__file__])
