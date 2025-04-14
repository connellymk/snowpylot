import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest

from snowpylot.caaml_parser import caaml_parser
from snowpylot.snow_pit import SnowPit
from snowpylot.stability_tests import (
    ComprTest,
    ExtColumnTest,
    PropSawTest,
    RBlockTest,
    StabilityTests,
)


@pytest.fixture
def test_pit():
    """Fixture to load the test snowpit file"""
    return caaml_parser("demos/snowpits/test/snowpylot-test-26-Feb-caaml.xml")


def test_stability_tests_structure(test_pit):
    """Test that StabilityTests object is properly structured"""
    stability_tests = test_pit.stability_tests
    assert isinstance(stability_tests, StabilityTests)
    assert isinstance(stability_tests.ECT, list)
    assert isinstance(stability_tests.CT, list)
    assert isinstance(stability_tests.RBlock, list)
    assert isinstance(stability_tests.PST, list)


def test_extended_column_tests(test_pit):
    """Test Extended Column Test parsing"""
    ects = test_pit.stability_tests.ECT
    assert len(ects) == 2

    # Test first ECT
    ect1 = ects[0]
    assert isinstance(ect1, ExtColumnTest)
    assert ect1.depth_top == [11.0, "cm"]
    assert ect1.test_score == "ECTN4"
    assert ect1.comment == "ECT 1 comment"

    # Test second ECT
    ect2 = ects[1]
    assert isinstance(ect2, ExtColumnTest)
    assert ect2.depth_top == [32.0, "cm"]
    assert ect2.test_score == "ECTN25"
    assert ect2.comment == "ECT 2 comment"


def test_compression_tests(test_pit):
    """Test Compression Test parsing"""
    cts = test_pit.stability_tests.CT
    assert len(cts) == 3

    # Test CT 1
    ct1 = cts[0]
    assert isinstance(ct1, ComprTest)
    assert ct1.depth_top == [11.0, "cm"]
    assert ct1.test_score == "13"
    assert ct1.fracture_character == "Q2"
    assert ct1.comment == "CT 2 comment"

    # Test CT 2
    ct2 = cts[1]
    assert ct2.test_score == "CTN"
    assert ct2.comment is None

    # Test CT 3
    ct3 = cts[2]
    assert ct3.depth_top == [94.0, "cm"]
    assert ct3.test_score == "28"
    assert ct3.fracture_character == "Q2"
    assert ct3.comment == "CT 3 comment"


def test_rutschblock_tests(test_pit):
    """Test Rutschblock Test parsing"""
    rbts = test_pit.stability_tests.RBlock
    assert len(rbts) == 1

    # Test RB
    rbt = rbts[0]
    assert isinstance(rbt, RBlockTest)
    assert rbt.depth_top == [120.0, "cm"]
    assert rbt.test_score == "RB3"
    assert rbt.fracture_character == "Q2"
    assert rbt.release_type == "MB"
    assert rbt.comment == "RBlock 1 comment"


def test_propagation_saw_tests(test_pit):
    """Test Propagation Saw Test parsing"""
    psts = test_pit.stability_tests.PST
    assert len(psts) == 1

    # Test PST
    pst = psts[0]
    assert isinstance(pst, PropSawTest)
    assert pst.depth_top == [65.0, "cm"]
    assert pst.fracture_prop == "Arr"
    assert pst.cut_length == [13.0, "cm"]
    assert pst.column_length == [100.0, "cm"]
    assert pst.comment == "shovel shear com"


def test_empty_test_lists(test_pit):
    """Test that unused test types are empty lists"""
    # Create a new test pit with no stability tests
    empty_pit = SnowPit()  # Create an empty pit instead of using a file
    empty_tests = empty_pit.stability_tests

    # Check that all test lists are empty
    assert len(empty_tests.ECT) == 0
    assert len(empty_tests.CT) == 0
    assert len(empty_tests.RBlock) == 0
    assert len(empty_tests.PST) == 0


def test_string_representation(test_pit):
    """Test string representation of stability tests"""
    stability_tests = test_pit.stability_tests
    str_rep = str(stability_tests)

    # Check that key information is in the string representation
    assert "depth_top: [11.0, 'cm']" in str_rep
    assert "test_score: ECTN4" in str_rep
    assert "fracture_character: Q2" in str_rep
    assert "fracture_prop: Arr" in str_rep
    assert "cut_length: [13.0, 'cm']" in str_rep
    assert "column_length: [100.0, 'cm']" in str_rep


if __name__ == "__main__":
    pytest.main([__file__])
