from dataclasses import dataclass, field
from typing import Optional, Tuple


@dataclass
class WeatherConditions:
    """
    WeatherConditions class for representing the weather conditions of a snow profile.

    Attributes:
        sky_cond: Sky condition code
        precip_ti: Precipitation type and intensity code
        air_temp_pres: Air temperature with unit
        wind_speed: Wind speed code
        wind_dir: Wind direction
        sky_cond_desc: Description of sky condition
        precip_ti_desc: Description of precipitation type and intensity
        wind_speed_desc: Description of wind speed
    """

    # Parsed properties
    sky_cond: Optional[str] = None
    precip_ti: Optional[str] = None
    air_temp_pres: Optional[Tuple[float, str]] = None
    wind_speed: Optional[str] = None
    wind_dir: Optional[str] = None

    # Computed properties
    sky_cond_desc: Optional[str] = None
    precip_ti_desc: Optional[str] = None
    wind_speed_desc: Optional[str] = None

    def __str__(self) -> str:
        """Return a string representation of the weather conditions."""
        return (
            f"\n\t sky_cond: {self.sky_cond}"
            f"\n\t sky_cond_desc: {self.sky_cond_desc}"
            f"\n\t precip_ti: {self.precip_ti}"
            f"\n\t precip_ti_desc: {self.precip_ti_desc}"
            f"\n\t air_temp_pres: {self.air_temp_pres}"
            f"\n\t wind_speed: {self.wind_speed}"
            f"\n\t wind_speed_desc: {self.wind_speed_desc}"
            f"\n\t wind_dir: {self.wind_dir}"
        )

    def set_sky_cond(self, sky_cond: str) -> None:
        """
        Set the sky condition and compute the description.

        Args:
            sky_cond: The sky condition code
        """
        self.sky_cond = sky_cond

        sky_cond_dict = {
            "CLR": "Clear",
            "FEW": "Few",
            "SCT": "Scattered",
            "BKN": "Broken",
            "OVC": "Overcast",
            "X": "Obscured",
        }

        self.sky_cond_desc = sky_cond_dict.get(sky_cond)

    def set_precip_ti(self, precip_ti: str) -> None:
        """
        Set the precipitation type and intensity and compute the description.

        Args:
            precip_ti: The precipitation type and intensity code
        """
        self.precip_ti = precip_ti

        precip_ti_dict = {
            "NIL": "None",
            "S-1": "Snow < 0.5 cm/hr",
            "S1": "Snow - 1 cm/hr",
            "S2": "Snow - 2 cm/hr",
            "S5": "Snow - 5 cm/hr",
            "S10": "Snow - 10 cm/hr",
            "G": "Graupel or hail",
            "RS": "Mixed rain and snow",
            "RV": "Very light rain - mist",
            "RL": "Light Rain < 2.5mm/hr",
            "RM": "Moderate rain < 7.5mm/hr",
            "RH": "Heavy rain > 7.5mm/hr",
        }

        self.precip_ti_desc = precip_ti_dict.get(precip_ti)

    def set_air_temp_pres(self, air_temp_pres: Tuple[float, str]) -> None:
        """
        Set the air temperature.

        Args:
            air_temp_pres: The air temperature with unit
        """
        self.air_temp_pres = air_temp_pres

    def set_wind_speed(self, wind_speed: str) -> None:
        """
        Set the wind speed and compute the description.

        Args:
            wind_speed: The wind speed code
        """
        self.wind_speed = wind_speed

        wind_speed_dict = {
            "C": "Calm",
            "L": "Light breeze",
            "M": "Moderate",
            "S": "Strong",
            "X": "gale force winds",
        }

        self.wind_speed_desc = wind_speed_dict.get(wind_speed)

    def set_wind_dir(self, wind_dir: str) -> None:
        """
        Set the wind direction.

        Args:
            wind_dir: The wind direction
        """
        self.wind_dir = wind_dir


@dataclass
class Location:
    """
    Location class for representing a location from a Snowpilot XML file.

    Attributes:
        latitude: Latitude
        longitude: Longitude
        elevation: Elevation with unit
        aspect: Aspect
        slope_angle: Slope angle with unit
        country: Country
        region: Region
        pit_near_avalanche: Whether the pit is near an avalanche
        pit_near_avalanche_location: Location of the pit relative to the avalanche
    """

    latitude: Optional[float] = None
    longitude: Optional[float] = None
    elevation: Optional[Tuple[float, str]] = None
    aspect: Optional[str] = None
    slope_angle: Optional[Tuple[float, str]] = None
    country: Optional[str] = None
    region: Optional[str] = None
    pit_near_avalanche: Optional[bool] = None
    pit_near_avalanche_location: Optional[str] = None

    def __str__(self) -> str:
        """Return a string representation of the location."""
        location_str = (
            f"latitude: {self.latitude}\n"
            f"longitude: {self.longitude}\n"
            f"elevation: {self.elevation}\n"
            f"aspect: {self.aspect}\n"
            f"slope_angle: {self.slope_angle}\n"
            f"country: {self.country}\n"
            f"region: {self.region}\n"
            f"pit_near_avalanche: {self.pit_near_avalanche}\n"
        )

        if self.pit_near_avalanche_location is not None:
            location_str += (
                f"pit_near_avalanche_location: {self.pit_near_avalanche_location}\n"
            )

        return location_str

    def set_latitude(self, latitude: float) -> None:
        """
        Set the latitude.

        Args:
            latitude: The latitude
        """
        self.latitude = latitude

    def set_longitude(self, longitude: float) -> None:
        """
        Set the longitude.

        Args:
            longitude: The longitude
        """
        self.longitude = longitude

    def set_elevation(self, elevation: Tuple[float, str]) -> None:
        """
        Set the elevation.

        Args:
            elevation: The elevation with unit
        """
        self.elevation = elevation

    def set_aspect(self, aspect: str) -> None:
        """
        Set the aspect.

        Args:
            aspect: The aspect
        """
        self.aspect = aspect

    def set_slope_angle(self, slope_angle: Tuple[float, str]) -> None:
        """
        Set the slope angle.

        Args:
            slope_angle: The slope angle with unit
        """
        self.slope_angle = slope_angle

    def set_country(self, country: str) -> None:
        """
        Set the country.

        Args:
            country: The country
        """
        self.country = country

    def set_region(self, region: str) -> None:
        """
        Set the region.

        Args:
            region: The region
        """
        self.region = region

    def set_pit_near_avalanche(self, pit_near_avalanche: bool) -> None:
        """
        Set whether the pit is near an avalanche.

        Args:
            pit_near_avalanche: Whether the pit is near an avalanche
        """
        self.pit_near_avalanche = pit_near_avalanche

    def set_pit_near_avalanche_location(self, pit_near_avalanche_location: str) -> None:
        """
        Set the location of the pit relative to the avalanche.

        Args:
            pit_near_avalanche_location: The location of the pit relative to the
                avalanche
        """
        self.pit_near_avalanche_location = pit_near_avalanche_location


@dataclass
class User:
    """
    User class for representing a Snow Pilot user.

    Attributes:
        operation_id: Operation ID
        operation_name: Operation name
        professional: Whether the user is a professional
        user_id: User ID
        username: Username
    """

    operation_id: Optional[str] = None
    operation_name: Optional[str] = None
    professional: bool = False
    user_id: Optional[str] = None
    username: Optional[str] = None

    def __str__(self) -> str:
        """Return a string representation of the user."""
        user_str = f"operation_id: {self.operation_id}\n"

        if self.operation_name is not None:
            user_str += f"operation_name: {self.operation_name}\n"

        user_str += (
            f"professional: {self.professional}\n"
            f"user_id: {self.user_id}\n"
            f"username: {self.username}\n"
        )

        return user_str

    def set_operation_id(self, operation_id: str) -> None:
        """
        Set the operation ID.

        Args:
            operation_id: The operation ID
        """
        self.operation_id = operation_id

    def set_operation_name(self, operation_name: str) -> None:
        """
        Set the operation name.

        Args:
            operation_name: The operation name
        """
        self.operation_name = operation_name

    def set_professional(self, professional: bool) -> None:
        """
        Set whether the user is a professional.

        Args:
            professional: Whether the user is a professional
        """
        self.professional = professional

    def set_user_id(self, user_id: str) -> None:
        """
        Set the user ID.

        Args:
            user_id: The user ID
        """
        self.user_id = user_id

    def set_username(self, username: str) -> None:
        """
        Set the username.

        Args:
            username: The username
        """
        self.username = username


@dataclass
class CoreInfo:
    """
    CoreInfo class for representing a "core Info" from a Snowpilot XML file.

    Attributes:
        pit_id: Pit ID
        pit_name: Pit name
        date: Date
        comment: Comment
        caaml_version: CAAML version
        user: User information
        location: Location information
        weather_conditions: Weather conditions
    """

    pit_id: Optional[str] = None
    pit_name: Optional[str] = None
    date: Optional[str] = None
    comment: Optional[str] = None
    caaml_version: Optional[str] = None
    user: User = field(default_factory=User)
    location: Location = field(default_factory=Location)
    weather_conditions: WeatherConditions = field(default_factory=WeatherConditions)

    def __str__(self) -> str:
        """Return a string representation of the core info."""
        return (
            f"pit_id: {self.pit_id}\n"
            f"pit_name: {self.pit_name}\n"
            f"date: {self.date}\n"
            f"comment: {self.comment}\n"
            f"caaml_version: {self.caaml_version}\n"
            f"user: {self.user}\n"
            f"location: {self.location}\n"
            f"weather_conditions: {self.weather_conditions}\n"
        )

    def set_pit_id(self, pit_id: str) -> None:
        """
        Set the pit ID.

        Args:
            pit_id: The pit ID
        """
        self.pit_id = pit_id

    def set_pit_name(self, pit_name: str) -> None:
        """
        Set the pit name.

        Args:
            pit_name: The pit name
        """
        self.pit_name = pit_name

    def set_date(self, date: str) -> None:
        """
        Set the date.

        Args:
            date: The date
        """
        self.date = date

    def set_comment(self, comment: str) -> None:
        """
        Set the comment.

        Args:
            comment: The comment
        """
        self.comment = comment

    def set_caaml_version(self, caaml_version: str) -> None:
        """
        Set the CAAML version.

        Args:
            caaml_version: The CAAML version
        """
        self.caaml_version = caaml_version
