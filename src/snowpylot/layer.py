from dataclasses import dataclass
from typing import Optional, Tuple


@dataclass
class Grain:
    """
    Grain class for representing a grain form in a snow layer.

    Attributes:
        grain_form: The grain form code
        grain_size_avg: Average grain size with unit
        grain_size_max: Maximum grain size with unit
        basic_grain_class_code: Basic grain class code
        basic_grain_class_name: Basic grain class name
        sub_grain_class_code: Sub grain class code
        sub_grain_class_name: Sub grain class name
    """

    grain_form: Optional[str] = None
    grain_size_avg: Optional[Tuple[float, str]] = None
    grain_size_max: Optional[Tuple[float, str]] = None
    basic_grain_class_code: Optional[str] = None
    basic_grain_class_name: Optional[str] = None
    sub_grain_class_code: Optional[str] = None
    sub_grain_class_name: Optional[str] = None

    def __str__(self) -> str:
        """Return a string representation of the grain."""
        return (
            f"\n\t\t grain_form: {self.grain_form}"
            f"\n\t\t grain_size_avg: {self.grain_size_avg}"
            f"\n\t\t grain_size_max: {self.grain_size_max}"
            f"\n\t\t basic_grain_class_code: {self.basic_grain_class_code}"
            f"\n\t\t basic_grain_class_name: {self.basic_grain_class_name}"
            f"\n\t\t sub_grain_class_code: {self.sub_grain_class_code}"
            f"\n\t\t sub_grain_class_name: {self.sub_grain_class_name}"
        )

    def set_grain_form(self, grain_form: str) -> None:
        """
        Set the grain form and compute derived properties.

        Args:
            grain_form: The grain form code
        """
        self.grain_form = grain_form

        # Basic grain class dictionary
        basic_grain_class_dict = {
            "PP": "Precipitation particles",
            "DF": "Decomposing and fragmented precipitation particles",
            "RG": "Rounded grains",
            "FC": "Faceted crystals",
            "DH": "Depth hoar",
            "SH": "Surface hoar",
            "MF": "Melt forms",
            "IF": "Ice formations",
            "MM": "Machine made Snow",
        }

        # Sub grain class dictionary
        sub_grain_class_dict = {
            "PPgp": "Graupel",
            "PPco": "Columns",
            "PPhl": "Hail",
            "PPpl": "Plates",
            "PPnd": "Needles",
            "PPsd": "Stellars, Dendrites",
            "PPir": "Irregular crystals",
            "PPip": "Ice pellets",
            "PPrm": "Rime",
            "DFdc": "Partly decomposed precipitation particles",
            "DFbk": "Wind-broken precipitation particles",
            "RGsr": "Small rounded particles",
            "RGlr": "Large rounded particles",
            "RGwp": "Wind packed",
            "RGxf": "Faceted rounded particles",
            "FCso": "Solid faceted particles",
            "FCsf": "Near surface faceted particles",
            "FCxr": "Rounding faceted particles",
            "DHcp": "Hollow cups",
            "DHpr": "Hollow prisms",
            "DHch": "Chains of depth hoar",
            "DHla": "Large striated crystals",
            "DHxr": "Rounding depth hoar",
            "SHsu": "Surface hoar crystals",
            "SHcv": "Cavity or crevasse hoar",
            "SHxr": "Rounding surface hoar",
            "MFcl": "Clustered rounded grains",
            "MFpc": "Rounded polycrystals",
            "MFsl": "Slush",
            "MFcr": "Melt-freeze crust",
            "IFil": "Ice layer",
            "IFic": "Ice column",
            "IFbi": "Basal ice",
            "IFrc": "Rain crust",
            "IFsc": "Sun crust",
            "MMrp": "Round polycrystalline particles",
            "MMci": "Crushed ice particles",
        }

        if len(grain_form) > 2:
            self.basic_grain_class_code = grain_form[:2]
            self.sub_grain_class_code = grain_form
            self.basic_grain_class_name = basic_grain_class_dict.get(
                self.basic_grain_class_code
            )
            self.sub_grain_class_name = sub_grain_class_dict.get(
                self.sub_grain_class_code
            )
        else:
            self.basic_grain_class_code = grain_form
            self.basic_grain_class_name = basic_grain_class_dict.get(
                self.basic_grain_class_code
            )

    def set_grain_size_avg(self, grain_size_avg: Tuple[float, str]) -> None:
        """
        Set the average grain size.

        Args:
            grain_size_avg: The average grain size with unit
        """
        self.grain_size_avg = grain_size_avg

    def set_grain_size_max(self, grain_size_max: Tuple[float, str]) -> None:
        """
        Set the maximum grain size.

        Args:
            grain_size_max: The maximum grain size with unit
        """
        self.grain_size_max = grain_size_max


@dataclass
class Layer:
    """
    Layer class for representing a snow layer in a snow profile.

    Attributes:
        depth_top: Depth from the surface to the top of the layer
        thickness: Thickness of the layer
        hardness: Hardness of the layer
        hardness_top: Hardness at the top of the layer
        hardness_bottom: Hardness at the bottom of the layer
        grain_form_primary: Primary grain form
        grain_form_secondary: Secondary grain form
        wetness: Wetness of the layer
        layer_of_concern: Whether the layer is of concern
        comments: Comments about the layer
    """

    depth_top: Optional[Tuple[float, str]] = None
    thickness: Optional[Tuple[float, str]] = None
    hardness: Optional[str] = None
    hardness_top: Optional[str] = None
    hardness_bottom: Optional[str] = None
    grain_form_primary: Optional[Grain] = None
    grain_form_secondary: Optional[Grain] = None
    wetness: Optional[str] = None
    layer_of_concern: Optional[bool] = None
    comments: Optional[str] = None

    # Computed properties
    wetness_desc: Optional[str] = None

    def __str__(self) -> str:
        """Return a string representation of the layer."""
        return (
            f"Layer:\n"
            f"\t depth_top: {self.depth_top}\n"
            f"\t thickness: {self.thickness}\n"
            f"\t hardness: {self.hardness}\n"
            f"\t hardness_top: {self.hardness_top}\n"
            f"\t hardness_bottom: {self.hardness_bottom}\n"
            f"\t grain_form_primary: {self.grain_form_primary}\n"
            f"\t grain_form_secondary: {self.grain_form_secondary}\n"
            f"\t wetness: {self.wetness}\n"
            f"\t layer_of_concern: {self.layer_of_concern}\n"
            f"\t wetness_desc: {self.wetness_desc}\n"
            f"\t comments: {self.comments}"
        )

    def set_depth_top(self, depth_top: Tuple[float, str]) -> None:
        """
        Set the depth from the surface to the top of the layer.

        Args:
            depth_top: The depth with unit
        """
        self.depth_top = depth_top

    def set_thickness(self, thickness: Tuple[float, str]) -> None:
        """
        Set the thickness of the layer.

        Args:
            thickness: The thickness with unit
        """
        self.thickness = thickness

    def set_hardness(self, hardness: str) -> None:
        """
        Set the hardness of the layer.

        Args:
            hardness: The hardness
        """
        self.hardness = hardness

    def set_hardness_top(self, hardness_top: str) -> None:
        """
        Set the hardness at the top of the layer.

        Args:
            hardness_top: The hardness at the top
        """
        self.hardness_top = hardness_top

    def set_hardness_bottom(self, hardness_bottom: str) -> None:
        """
        Set the hardness at the bottom of the layer.

        Args:
            hardness_bottom: The hardness at the bottom
        """
        self.hardness_bottom = hardness_bottom

    def set_wetness(self, wetness: str) -> None:
        """
        Set the wetness of the layer and compute the description.

        Args:
            wetness: The wetness
        """
        self.wetness = wetness

        wetness_dict = {
            "D": "Dry",
            "D-M": "Dry to moist",
            "M": "Moist",
            "M-W": "Moist to wet",
            "W": "Wet",
            "W-VW": "Wet to very wet",
            "VW": "Very wet",
            "VW-S": "Very wet to slush",
            "S": "Slush",
        }

        self.wetness_desc = wetness_dict.get(wetness)

    def set_layer_of_concern(self, layer_of_concern: bool) -> None:
        """
        Set whether the layer is of concern.

        Args:
            layer_of_concern: Whether the layer is of concern
        """
        self.layer_of_concern = layer_of_concern

    def set_comments(self, comments: str) -> None:
        """
        Set comments about the layer.

        Args:
            comments: The comments
        """
        self.comments = comments
