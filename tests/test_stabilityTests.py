import os
import sys

import pytest

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from snowpylot.caaml_parser import caaml_parser
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
    return caaml_parser("snowpits/test/snowpylot-test-26-Feb-caaml.xml")


def test_stability_tests_structure(test_pit):
    """Test that StabilityTests object is properly structured"""
    stability_tests = test_pit.stabilityTests
    assert isinstance(stability_tests, StabilityTests)
    assert isinstance(stability_tests.ECT, list)
    assert isinstance(stability_tests.CT, list)
    assert isinstance(stability_tests.RBlock, list)
    assert isinstance(stability_tests.PST, list)
    assert isinstance(stability_tests.SBT, list)
    assert isinstance(stability_tests.SST, list)
    assert isinstance(stability_tests.DTT, list)


def test_extended_column_tests(test_pit):
    """Test Extended Column Test parsing"""
    ects = test_pit.stabilityTests.ECT
    assert len(ects) == 2

    # Test first ECT
    ect1 = ects[0]
    assert isinstance(ect1, ExtColumnTest)
    assert ect1.depthTop == [11.0, "cm"]
    assert ect1.testScore == "ECTN4"
    assert ect1.propogation is False
    assert ect1.numTaps == "4"
    # assert ect1.comment == "ECT 1 comment"

    # Test second ECT
    ect2 = ects[1]
    assert ect2.depthTop == [32.0, "cm"]
    assert ect2.testScore == "ECTN25"
    assert ect2.propogation is False
    assert ect2.numTaps == "25"
    # assert ect2.comment == "ECT 2 comment"


def test_compression_tests(test_pit):
    """Test Compression Test parsing"""
    cts = test_pit.stabilityTests.CT
    assert len(cts) == 3

    # Test first CT
    ct1 = cts[0]
    assert isinstance(ct1, ComprTest)
    assert ct1.depthTop == [11.0, "cm"]
    assert ct1.testScore == "13"
    assert ct1.fractureCharacter == "Q2"
    # assert ct1.comment == "CT comment 1"

    # Test second CT (no failure)
    ct2 = cts[1]
    assert ct2.testScore == "CTN"

    # Test third CT
    ct3 = cts[2]
    assert ct3.depthTop == [94.0, "cm"]
    assert ct3.testScore == "28"
    assert ct3.fractureCharacter == "Q2"
    # assert ct3.comment == "CT 3 comment"


def test_rutschblock_tests(test_pit):
    """Test Rutschblock Test parsing"""
    rbts = test_pit.stabilityTests.RBlock
    assert len(rbts) == 1

    rbt = rbts[0]
    assert isinstance(rbt, RBlockTest)
    assert rbt.depthTop == [120.0, "cm"]
    assert rbt.testScore == "RB3"
    assert rbt.releaseType == "MB"
    assert rbt.fractureCharacter == "Q2"
    # assert rbt.comment == "RBlock 1 comment"


def test_propagation_saw_tests(test_pit):
    """Test Propagation Saw Test parsing"""
    psts = test_pit.stabilityTests.PST
    assert len(psts) == 1

    pst = psts[0]
    assert isinstance(pst, PropSawTest)
    assert pst.depthTop == [65.0, "cm"]
    assert pst.fractureProp == "Arr"
    assert pst.cutLength == [13.0, "cm"]
    assert pst.columnLength == [100.0, "cm"]
    # assert pst.comment == "PST comment"


def test_empty_test_lists(test_pit):
    """Test that unused test types are empty lists"""
    stability_tests = test_pit.stabilityTests
    assert len(stability_tests.SBT) == 0
    assert len(stability_tests.SST) == 0
    assert len(stability_tests.DTT) == 0


def test_string_representation(test_pit):
    """Test string representation of StabilityTests objects"""
    stability_tests = test_pit.stabilityTests
    str_repr = str(stability_tests)

    # Check that test results are included in string representation
    assert "ExtColumnTest 1" in str_repr
    assert "CompressionTest 1" in str_repr
    assert "RutschblockTest 1" in str_repr
    assert "PropSawTest 1" in str_repr

    # Test individual test string representations
    ect_str = str(stability_tests.ECT[0])
    assert "depthTop: [11.0, 'cm']" in ect_str
    assert "testScore: ECTN4" in ect_str
    assert "propogation: False" in ect_str

    ct_str = str(stability_tests.CT[0])
    assert "depthTop: [11.0, 'cm']" in ct_str
    assert "testScore: 13" in ct_str
    assert "fractureCharacter: Q2" in ct_str

    rbt_str = str(stability_tests.RBlock[0])
    assert "depthTop: [120.0, 'cm']" in rbt_str
    assert "testScore: RB3" in rbt_str
    assert "releaseType: MB" in rbt_str

    pst_str = str(stability_tests.PST[0])
    assert "depthTop: [65.0, 'cm']" in pst_str
    assert "fractureProp: Arr" in pst_str
    assert "cutLength: [13.0, 'cm']" in pst_str


if __name__ == "__main__":
    pytest.main([__file__])
