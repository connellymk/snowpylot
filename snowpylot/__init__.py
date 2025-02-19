"""
This module provides classes and functions for parsing and analyzing SnowPilot caaml.xml files.

The module includes the following classes:
- Layer: Represents a layer of snow in a snow pit.
- SnowProfile: Includes a list of layers, surface condition, and temperature profile.
- StabilityTests: Represents the stability tests performed on a snow profile.
- SnowPit: Represents a snow pit observation.

The module includes the following functions:
- caaml_parser: Parses a SnowPilot caaml.xml file and returns a SnowPit object.

"""


# Import Classes
from snowpylot.layer import Layer
from snowpylot.snowProfile import SnowProfile, SurfaceCondition, TempMeasurement
from snowpylot.stabilityTests import (
    StabilityTests,
    ExtColumnTest,
    ComprTest,
    RutschblockTest,
    PropSawTest,
    StuffBlockTest,
    ShovelShearTest,
    DeepTapTest
)
from snowpylot.snowPit import SnowPit

# Import Functions
from snowpylot.caaml_parser import caaml_parser

__version__ = '0.1.0'

__all__ = [
    'Layer',
    'SnowPit',
    'SnowProfile',
    'SurfaceCondition',
    'TempMeasurement',
    'StabilityTests',
    'ExtColumnTest',
    'ComprTest',
    'RutschblockTest',
    'PropSawTest',
    'StuffBlockTest',
    'ShovelShearTest',
    'DeepTapTest',
    'caaml_parser'
]