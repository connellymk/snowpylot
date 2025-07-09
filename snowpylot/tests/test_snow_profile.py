import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest

from snowpylot.caaml_parser import caaml_parser


@pytest.fixture
def test_pit():
    """Fixture to load the test snowpit file"""
    return caaml_parser("demos/snowpits/test/snowpylot-test-26-Feb-caaml.xml")


def test_snow_profile_structure(test_pit):
    """Test that SnowProfile object is properly structured"""
    profile = test_pit.snow_profile
    assert profile is not None
    assert profile.surf_cond is not None
    assert profile.layers is not None
    assert profile.temp_profile is not None


def test_basic_profile_info(test_pit):
    """Test basic snow profile information"""
    profile = test_pit.snow_profile
    assert profile.measurement_direction == "top down"
    assert profile.profile_depth == [155.0, "cm"]
    assert profile.hs == [155.0, "cm"]


def test_surface_conditions(test_pit):
    """Test surface conditions parsing"""
    surface = test_pit.snow_profile.surf_cond
    assert surface.wind_loading == "previous"
    assert surface.penetration_foot == [60.0, "cm"]
    assert surface.penetration_ski == [20.0, "cm"]


def test_layers(test_pit):
    """Test snow layers parsing"""
    layers = test_pit.snow_profile.layers
    assert len(layers) == 11  # Test file has 11 layers

    # Test first layer
    layer1 = layers[0]
    assert layer1.depth_top == [0.0, "cm"]
    assert layer1.thickness == [11.0, "cm"]
    assert layer1.hardness == "F"
    assert layer1.wetness == "D-M"
    assert layer1.grain_form_primary.grain_form == "RG"
    assert layer1.grain_form_secondary.grain_form == "DF"
    assert layer1.grain_form_primary.grain_size_avg == [0.5, "mm"]
    assert layer1.comments == "layer 1 comment"

    # Test middle layer (layer 7) - layer of concern
    layer7 = layers[6]
    assert layer7.depth_top == [66.0, "cm"]
    assert layer7.thickness == [5.0, "cm"]
    assert layer7.hardness == "1F"
    assert layer7.wetness == "D"
    assert layer7.grain_form_primary.grain_form == "SHxr"
    assert layer7.grain_form_secondary.grain_form == "FCxr"
    assert layer7.layer_of_concern is True
    assert layer7.comments == "layer 7 comment"

    # Test last layer
    layer11 = layers[-1]
    assert layer11.depth_top == [125.0, "cm"]
    assert layer11.thickness == [30.0, "cm"]
    assert layer11.hardness == "1F"
    assert layer11.wetness == "D"
    assert layer11.grain_form_primary.grain_form == "FCxr"
    assert layer11.grain_form_primary.grain_size_avg == [2.0, "mm"]
    assert layer11.comments == "layer 11 comment"


def test_temperature_profile(test_pit):
    """Test temperature profile parsing"""
    temps = test_pit.snow_profile.temp_profile
    assert len(temps) == 16  # Test file has 16 temperature measurements

    # Test first temperature measurement
    assert temps[0].depth == [0.0, "cm"]
    assert temps[0].snow_temp == [-2.22, "degC"]

    # Test middle temperature measurement
    assert temps[7].depth == [65.0, "cm"]
    assert temps[7].snow_temp == [-2.78, "degC"]

    # Test last temperature measurement
    assert temps[-1].depth == [145.0, "cm"]
    assert temps[-1].snow_temp == [-2.22, "degC"]


def test_grain_form_classification(test_pit):
    """Test grain form classification parsing"""
    layers = test_pit.snow_profile.layers

    # Test different grain forms and their classifications
    grain_tests = [
        (layers[0].grain_form_primary, "RG", "Rounded grains"),  # Layer 1
        (layers[6].grain_form_primary, "SHxr", "Surface hoar"),  # Layer 7
        (layers[9].grain_form_primary, "FCso", "Faceted crystals"),  # Layer 10
    ]

    for grain, expected_code, expected_class in grain_tests:
        assert grain.grain_form == expected_code
        assert grain.basic_grain_class_name == expected_class


def test_layer_of_concern(test_pit):
    """Test layer of concern identification"""
    profile = test_pit.snow_profile
    assert profile.layer_of_concern is not None
    assert profile.layer_of_concern.depth_top == [66.0, "cm"]
    assert profile.layer_of_concern.grain_form_primary.grain_form == "SHxr"
    assert profile.layer_of_concern.hardness == "1F"


def test_string_representation(test_pit):
    """Test string representation of SnowProfile objects"""
    profile = test_pit.snow_profile
    str_repr = str(profile)

    # Check that important fields are included in string representation
    assert "measurement_direction: top down" in str_repr
    assert "profile_depth: [155.0, 'cm']" in str_repr
    assert "Layer" in str_repr
    assert "temp_profile" in str_repr

    # Test layer string representation
    layer_str = str(profile.layers[0])
    assert "\n\t depth_top: [0.0, 'cm']" in layer_str  # Updated to match exact format
    assert "\n\t thickness: [11.0, 'cm']" in layer_str  # Updated to match exact format
    assert "\n\t grain_form_primary" in layer_str

    # Test temperature observation string representation
    temp_str = str(profile.temp_profile[0])
    assert "depth: [0.0, 'cm']" in temp_str
    assert "snow_temp: [-2.22, 'degC']" in temp_str


if __name__ == "__main__":
    pytest.main([__file__])
