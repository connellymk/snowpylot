from dataclasses import dataclass, field
from typing import List, Optional, Tuple

from .layer import Layer


@dataclass
class SurfaceCondition:
    """
    SurfaceCondition class for representing the surface condition of a snow profile.

    Attributes:
        wind_loading: Wind loading
        penetration_foot: Penetration of foot with unit
        penetration_ski: Penetration of ski with unit
    """

    wind_loading: Optional[str] = None
    penetration_foot: Optional[Tuple[float, str]] = None
    penetration_ski: Optional[Tuple[float, str]] = None

    def __str__(self) -> str:
        """Return a string representation of the surface condition."""
        return (
            f"\n\t wind_loading: {self.wind_loading}"
            f"\n\t penetration_foot: {self.penetration_foot}"
            f"\n\t penetration_ski: {self.penetration_ski}"
        )

    def set_wind_loading(self, wind_loading: str) -> None:
        """
        Set the wind loading.

        Args:
            wind_loading: The wind loading
        """
        self.wind_loading = wind_loading

    def set_penetration_foot(self, penetration_foot: Tuple[float, str]) -> None:
        """
        Set the penetration of foot.

        Args:
            penetration_foot: The penetration of foot with unit
        """
        self.penetration_foot = penetration_foot

    def set_penetration_ski(self, penetration_ski: Tuple[float, str]) -> None:
        """
        Set the penetration of ski.

        Args:
            penetration_ski: The penetration of ski with unit
        """
        self.penetration_ski = penetration_ski


@dataclass
class TempObs:
    """
    TempObs class for representing a temperature observation.

    Attributes:
        depth: Depth with unit
        snow_temp: Snow temperature with unit
    """

    depth: Optional[Tuple[float, str]] = None
    snow_temp: Optional[Tuple[float, str]] = None

    def __str__(self) -> str:
        """Return a string representation of the temperature observation."""
        return f"\n\t depth: {self.depth}\n\t snow_temp: {self.snow_temp}"

    def set_depth(self, depth: Tuple[float, str]) -> None:
        """
        Set the depth.

        Args:
            depth: The depth with unit
        """
        self.depth = depth

    def set_snow_temp(self, snow_temp: Tuple[float, str]) -> None:
        """
        Set the snow temperature.

        Args:
            snow_temp: The snow temperature with unit
        """
        self.snow_temp = snow_temp


@dataclass
class DensityObs:
    """
    DensityObs class for representing a density observation.

    Attributes:
        depth_top: Depth from the surface to the top of the layer with unit
        thickness: Thickness of the layer with unit
        density: Density with unit
    """

    depth_top: Optional[Tuple[float, str]] = None
    thickness: Optional[Tuple[float, str]] = None
    density: Optional[Tuple[float, str]] = None

    def __str__(self) -> str:
        """Return a string representation of the density observation."""
        return (
            f"\n\t depth_top: {self.depth_top}"
            f"\n\t thickness: {self.thickness}"
            f"\n\t density: {self.density}"
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

    def set_density(self, density: Tuple[float, str]) -> None:
        """
        Set the density.

        Args:
            density: The density with unit
        """
        self.density = density


@dataclass
class SnowProfile:
    """
    SnowProfile class for representing a snow profile.

    Attributes:
        measurement_direction: Measurement direction
        profile_depth: Profile depth with unit
        hs: Snow height with unit
        surf_cond: Surface condition
        layers: List of layers
        temp_profile: List of temperature observations
        density_profile: List of density observations
        layer_of_concern: Layer of concern
    """

    # Parsed properties
    measurement_direction: Optional[str] = None
    profile_depth: Optional[Tuple[float, str]] = None
    hs: Optional[Tuple[float, str]] = None
    surf_cond: Optional[SurfaceCondition] = None
    layers: List[Layer] = field(default_factory=list)
    temp_profile: List[TempObs] = field(default_factory=list)
    density_profile: List[DensityObs] = field(default_factory=list)

    # Computed properties
    layer_of_concern: Optional[Layer] = None

    def __str__(self) -> str:
        """Return a string representation of the snow profile."""
        snow_profile_str = (
            f"\n    measurement_direction: {self.measurement_direction}"
            f"\n    profile_depth: {self.profile_depth}"
            f"\n    hs: {self.hs}"
            f"\n    surf_cond: {self.surf_cond}"
            f"\n    Layers:"
        )

        if self.layers:
            for i, layer in enumerate(self.layers):
                snow_profile_str += f"\n    Layer {i + 1}: {layer}"

        snow_profile_str += "\n    temp_profile:"
        if self.temp_profile:
            for i, temp in enumerate(self.temp_profile):
                snow_profile_str += f"\n    temp {i + 1}: {temp}"

        snow_profile_str += "\n    density_profile:"
        if self.density_profile:
            for i, density in enumerate(self.density_profile):
                snow_profile_str += f"\n    density {i + 1}: {density}"

        snow_profile_str += f"\n    layer_of_concern: {self.layer_of_concern}"

        return snow_profile_str

    def set_measurement_direction(self, measurement_direction: str) -> None:
        """
        Set the measurement direction.

        Args:
            measurement_direction: The measurement direction
        """
        self.measurement_direction = measurement_direction

    def set_profile_depth(self, profile_depth: Tuple[float, str]) -> None:
        """
        Set the profile depth.

        Args:
            profile_depth: The profile depth with unit
        """
        self.profile_depth = profile_depth

    def set_hs(self, hs: Tuple[float, str]) -> None:
        """
        Set the snow height.

        Args:
            hs: The snow height with unit
        """
        self.hs = hs

    def set_surf_cond(self, surf_cond: SurfaceCondition) -> None:
        """
        Set the surface condition.

        Args:
            surf_cond: The surface condition
        """
        self.surf_cond = surf_cond

    def add_layer(self, layer: Layer) -> None:
        """
        Add a layer to the snow profile.

        Args:
            layer: The layer to add
        """
        self.layers.append(layer)
        if layer.layer_of_concern:
            self.layer_of_concern = layer

    def add_temp_obs(self, temp_obs: TempObs) -> None:
        """
        Add a temperature observation to the snow profile.

        Args:
            temp_obs: The temperature observation to add
        """
        self.temp_profile.append(temp_obs)

    def add_density_obs(self, density_obs: DensityObs) -> None:
        """
        Add a density observation to the snow profile.

        Args:
            density_obs: The density observation to add
        """
        self.density_profile.append(density_obs)
