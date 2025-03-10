"""
SnowPylot - A Python library for working with CAAML snow profile data
"""

from .caaml_parser import caaml_parser
from .snowPit import SnowPit
from .coreInfo import CoreInfo, User, Location, WeatherConditions
from .layer import Layer, Grain
from .snowProfile import SnowProfile, SurfaceCondition, TempObs, DensityObs
from .stabilityTests import (
    StabilityTests,
    ExtColumnTest,
    ComprTest,
    RBlockTest,
    PropSawTest,
)
from .whumpfData import WhumpfData

__version__ = "1.0.0"
