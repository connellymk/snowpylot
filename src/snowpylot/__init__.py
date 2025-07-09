"""
SnowPylot - A Python library for working with CAAML snow profile data
"""

__version__ = "1.1.3"

from .caaml_parser import caaml_parser
from .snow_pit import SnowPit

__all__ = ["SnowPit", "caaml_parser"]
