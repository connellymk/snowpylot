import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from snowpylot.caaml_parser import caaml_parser
from snowpylot.layer import Grain
from snowpylot.snow_profile import SnowProfile, SurfaceCondition


@pytest.fixture
def test_pit():
    """Fixture to load the test snowpit file"""
    return caaml_parser("snowpits/test/snowpylot-test-26-Feb-caaml.xml")


def test_snow_profile_structure(test_pit):
    """Test that SnowProfile object is properly structured"""
    profile = test_pit.snowProfile
    assert isinstance(profile, SnowProfile)
    assert isinstance(profile.surfCond, SurfaceCondition)
    assert isinstance(profile.layers, list)
    assert isinstance(profile.tempProfile, list)
    assert profile.densityProfile is None  # No density measurements in test file


def test_basic_profile_info(test_pit):
    """Test basic snow profile information"""
    profile = test_pit.snowProfile
    assert profile.measurementDirection == "top down"
    assert profile.profileDepth == [155.0, "cm"]
    assert profile.hS == [155.0, "cm"]


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
    assert layer1.depthTop == [0.0, "cm"]
    assert layer1.thickness == [11.0, "cm"]
    assert layer1.hardness == "F"
    assert layer1.wetness == "D-M"
    assert isinstance(layer1.grainFormPrimary, Grain)
    assert layer1.grainFormPrimary.grainForm == "RG"
    assert layer1.grainFormSecondary.grainForm == "DF"
    assert layer1.grainFormPrimary.grainSizeAvg == [0.5, "mm"]
    assert layer1.comments == "layer 1 comment"

    # Test middle layer (layer 7) - layer of concern
    layer7 = layers[6]
    assert layer7.depthTop == [66.0, "cm"]
    assert layer7.thickness == [5.0, "cm"]
    assert layer7.hardness == "1F"
    assert layer7.wetness == "D"
    assert layer7.grainFormPrimary.grainForm == "SHxr"
    assert layer7.grainFormSecondary.grainForm == "FCxr"
    assert layer7.layerOfConcern == "true"
    assert layer7.comments == "layer 7 comment"

    # Test last layer
    layer11 = layers[-1]
    assert layer11.depthTop == [125.0, "cm"]
    assert layer11.thickness == [30.0, "cm"]
    assert layer11.hardness == "1F"
    assert layer11.wetness == "D"
    assert layer11.grainFormPrimary.grainForm == "FCxr"
    assert layer11.grainFormPrimary.grainSizeAvg == [2.0, "mm"]
    assert layer11.comments == "layer 11 comment"


def test_temperature_profile(test_pit):
    """Test temperature profile parsing"""
    temps = test_pit.snowProfile.tempProfile
    assert len(temps) == 16  # Test file has 16 temperature measurements

    # Test first temperature measurement
    assert temps[0].depth == [0.0, "cm"]
    assert temps[0].snowTemp == [-2.22, "degC"]

    # Test middle temperature measurement
    assert temps[7].depth == [65.0, "cm"]
    assert temps[7].snowTemp == [-2.78, "degC"]

    # Test last temperature measurement
    assert temps[-1].depth == [145.0, "cm"]
    assert temps[-1].snowTemp == [-2.22, "degC"]


def test_grain_form_classification(test_pit):
    """Test grain form classification parsing"""
    layers = test_pit.snowProfile.layers

    # Test different grain forms and their classifications
    grain_tests = [
        (layers[0].grainFormPrimary, "RG", "Rounded grains"),  # Layer 1
        (layers[6].grainFormPrimary, "SHxr", "Surface hoar"),  # Layer 7
        (layers[9].grainFormPrimary, "FCso", "Faceted crystals"),  # Layer 10
    ]

    for grain, expected_code, expected_class in grain_tests:
        assert grain.grainForm == expected_code
        assert grain.basicGrainClass_name == expected_class


def test_layer_of_concern(test_pit):
    """Test layer of concern identification"""
    profile = test_pit.snowProfile
    assert profile.layer_of_concern is not None
    assert profile.layer_of_concern.depthTop == [66, "cm"]
    assert profile.layer_of_concern.grainFormPrimary.grainForm == "SHxr"


def test_string_representation(test_pit):
    """Test string representation of SnowProfile objects"""
    profile = test_pit.snowProfile
    str_repr = str(profile)

    # Check that important fields are included in string representation
    assert "measurementDirection: top down" in str_repr
    assert "profileDepth: [155.0, 'cm']" in str_repr
    assert "Layer" in str_repr
    assert "tempProfile" in str_repr

    # Test layer string representation
    layer_str = str(profile.layers[0])
    assert "\n\t depthTop: [0.0, 'cm']" in layer_str  # Updated to match exact format
    assert "\n\t thickness: [11.0, 'cm']" in layer_str  # Updated to match exact format
    assert "\n\t grainFormPrimary" in layer_str

    # Test temperature observation string representation
    temp_str = str(profile.tempProfile[0])
    assert "depth: [0.0, 'cm']" in temp_str
    assert "snowTemp: [-2.22, 'degC']" in temp_str


if __name__ == "__main__":
    pytest.main([__file__])
