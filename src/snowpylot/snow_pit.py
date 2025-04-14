from dataclasses import dataclass, field

from .core_info import CoreInfo
from .snow_profile import SnowProfile
from .stability_tests import StabilityTests
from .whumpf_data import WhumpfData


@dataclass
class SnowPit:
    """
    SnowPit class for representing a single snow pit observation.

    Attributes:
        core_info: Core information about the snow pit
        snow_profile: Snow profile information
        stability_tests: Stability test results
        whumpf_data: Whumpf data information
    """

    core_info: CoreInfo = field(default_factory=CoreInfo)
    snow_profile: SnowProfile = field(default_factory=SnowProfile)
    stability_tests: StabilityTests = field(default_factory=StabilityTests)
    whumpf_data: WhumpfData = field(default_factory=WhumpfData)

    def __str__(self) -> str:
        """Return a string representation of the snow pit."""
        return (
            f"SnowPit:\n"
            f"Core Info: {self.core_info}\n"
            f"Snow Profile: {self.snow_profile}\n"
            f"Stability Tests: {self.stability_tests}\n"
            f"Whumpf Data: {self.whumpf_data}\n"
        )
