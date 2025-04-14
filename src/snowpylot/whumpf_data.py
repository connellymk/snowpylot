from dataclasses import dataclass
from typing import Optional


@dataclass
class WhumpfData:
    """
    WhumpfData class for representing custom whumpf data.

    Attributes:
        whumpf_cracking: Whether there was whumpf cracking
        whumpf_no_cracking: Whether there was whumpf without cracking
        cracking_no_whumpf: Whether there was cracking without whumpf
        whumpf_near_pit: Whether there was whumpf near the pit
        whumpf_depth_weak_layer: Depth of the weak layer in whumpf
        whumpf_triggered_remote_ava: Whether whumpf triggered a remote avalanche
        whumpf_size: Size of the whumpf
    """

    whumpf_cracking: Optional[str] = None
    whumpf_no_cracking: Optional[str] = None
    cracking_no_whumpf: Optional[str] = None
    whumpf_near_pit: Optional[str] = None
    whumpf_depth_weak_layer: Optional[str] = None
    whumpf_triggered_remote_ava: Optional[str] = None
    whumpf_size: Optional[str] = None

    def __str__(self) -> str:
        """Return a string representation of the whumpf data."""
        return (
            f"\n\t whumpf_cracking: {self.whumpf_cracking}"
            f"\n\t whumpf_no_cracking: {self.whumpf_no_cracking}"
            f"\n\t cracking_no_whumpf: {self.cracking_no_whumpf}"
            f"\n\t whumpf_near_pit: {self.whumpf_near_pit}"
            f"\n\t whumpf_depth_weak_layer: {self.whumpf_depth_weak_layer}"
            f"\n\t whumpf_triggered_remote_ava: {self.whumpf_triggered_remote_ava}"
            f"\n\t whumpf_size: {self.whumpf_size}"
        )

    def set_whumpf_cracking(self, whumpf_cracking: str) -> None:
        """Set the whumpf cracking value."""
        self.whumpf_cracking = whumpf_cracking

    def set_whumpf_no_cracking(self, whumpf_no_cracking: str) -> None:
        """Set the whumpf no cracking value."""
        self.whumpf_no_cracking = whumpf_no_cracking

    def set_cracking_no_whumpf(self, cracking_no_whumpf: str) -> None:
        """Set the cracking no whumpf value."""
        self.cracking_no_whumpf = cracking_no_whumpf

    def set_whumpf_near_pit(self, whumpf_near_pit: str) -> None:
        """Set the whumpf near pit value."""
        self.whumpf_near_pit = whumpf_near_pit

    def set_whumpf_depth_weak_layer(self, whumpf_depth_weak_layer: str) -> None:
        """Set the whumpf depth weak layer value."""
        self.whumpf_depth_weak_layer = whumpf_depth_weak_layer

    def set_whumpf_triggered_remote_ava(self, whumpf_triggered_remote_ava: str) -> None:
        """Set the whumpf triggered remote avalanche value."""
        self.whumpf_triggered_remote_ava = whumpf_triggered_remote_ava

    def set_whumpf_size(self, whumpf_size: str) -> None:
        """Set the whumpf size value."""
        self.whumpf_size = whumpf_size
