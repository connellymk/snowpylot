class CoreInfo:
    """
    CoreInfo class for representing a "core Info" from a Snowpilot XML file. Includes the pitID, snowPitName, date, user, location, and weather.
    """

    def __init__(self):
        self.pitID = None
        self.pitName = None
        self.date = None
        self.comment = None
        self.caamlVersion = None
        self.user = User()
        self.location = Location()
        self.weatherConditions = WeatherConditions()

    def __str__(self):
        coreInfo_str = ""
        coreInfo_str += f"PitID: {self.pitID}\n"
        coreInfo_str += f"PitName: {self.pitName}\n"
        coreInfo_str += f"Date: {self.date}\n"
        coreInfo_str += f"Comment: {self.comment}\n"
        coreInfo_str += f"CAAML Version: {self.caamlVersion}\n"
        coreInfo_str += f"User: {self.user}\n"
        coreInfo_str += f"Location: {self.location}\n"
        coreInfo_str += f"WeatherConditions: {self.weatherConditions}\n"
        return coreInfo_str

    # Setters
    def set_pitID(self, pitID):
        self.pitID = pitID

    def set_pitName(self, pitName):
        self.pitName = pitName

    def set_date(self, date):
        self.date = date

    def set_comment(self, comment):
        self.comment = comment

    def set_caamlVersion(self, caamlVersion):
        self.caamlVersion = caamlVersion


class User:
    """
    User class for representing a Snow Pilot user
    """

    def __init__(self):
        self.operationID = None
        self.operationName = None
        self.professional = False  # default to false
        self.userID = None
        self.username = None

    def __str__(self):
        user_str = ""
        user_str += f"OperationID: {self.operationID}\n"
        if self.operationName is not None:
            user_str += f"OperationName: {self.operationName}\n"
        user_str += f"Professional: {self.professional}\n"
        user_str += f"UserID: {self.userID}\n"
        user_str += f"Username: {self.username}\n"
        return user_str

    # Setters
    def set_operationID(self, operationID):
        self.operationID = operationID

    def set_operationName(self, operationName):
        self.operationName = operationName

    def set_professional(self, professional):
        self.professional = professional

    def set_userID(self, userID):
        self.userID = userID

    def set_username(self, username):
        self.username = username


class Location:
    """
    Location class for representing a location from a Snowpilot XML file
    """

    def __init__(self):
        self.latitude = None
        self.longitude = None
        self.elevation = None
        self.aspect = None
        self.slopeAngle = None
        self.country = None
        self.region = None
        self.pitNearAvalanche = None
        self.pitNearAvalancheLocation = None

    def __str__(self):
        location_str = ""
        location_str += f"Latitude: {self.latitude}\n"
        location_str += f"Longitude: {self.longitude}\n"
        location_str += f"Elevation: {self.elevation}\n"
        location_str += f"Aspect: {self.aspect}\n"
        location_str += f"SlopeAngle: {self.slopeAngle}\n"
        location_str += f"Country: {self.country}\n"
        location_str += f"Region: {self.region}\n"
        location_str += f"PitNearAvalanche: {self.pitNearAvalanche}\n"
        if self.pitNearAvalancheLocation is not None:
            location_str += (
                f"PitNearAvalancheLocation: {self.pitNearAvalancheLocation}\n"
            )
        return location_str

    # Setters
    def set_latitude(self, latitude):
        self.latitude = latitude

    def set_longitude(self, longitude):
        self.longitude = longitude

    def set_elevation(self, elevation):
        self.elevation = elevation

    def set_aspect(self, aspect):
        self.aspect = aspect

    def set_slopeAngle(self, slopeAngle):
        self.slopeAngle = slopeAngle

    def set_country(self, country):
        self.country = country

    def set_region(self, region):
        self.region = region

    def set_pitNearAvalanche(self, pitNearAvalanche):
        self.pitNearAvalanche = pitNearAvalanche

    def set_pitNearAvalancheLocation(self, pitNearAvalancheLocation):
        self.pitNearAvalancheLocation = pitNearAvalancheLocation


class WeatherConditions:
    """
    WeatherConditions class for representing the weather conditions of a snow profile from a SnowPilot caaml.xml file
    """

    def __init__(self):
        # Parsed properties
        self.skyCond = None
        self.precipTI = None
        self.airTempPres = None
        self.windSpeed = None
        self.windDir = None
        # Computed properties
        self.skyCond_Desc = None
        self.precipTI_Desc = None
        self.windSpeed_Desc = None

    def __str__(self):
        weatherConditions_str = ""
        weatherConditions_str += f"\n\t skyCond: {self.skyCond}"
        weatherConditions_str += f"\n\t skyCond_Desc: {self.skyCond_Desc}"
        weatherConditions_str += f"\n\t precipTI: {self.precipTI}"
        weatherConditions_str += f"\n\t precipTI_Desc: {self.precipTI_Desc}"
        weatherConditions_str += f"\n\t airTempPres: {self.airTempPres}"
        weatherConditions_str += f"\n\t windSpeed: {self.windSpeed}"
        weatherConditions_str += f"\n\t windSpeed_Desc: {self.windSpeed_Desc}"
        weatherConditions_str += f"\n\t windDir: {self.windDir}"
        return weatherConditions_str

    # Setters
    def set_skyCond(self, skyCond):
        self.skyCond = skyCond

        skyCond_dict = {
            "CLR": "Clear",
            "FEW": "Few",
            "SCT": "Scattered",
            "BKN": "Broken",
            "OVC": "Overcast",
            "X": "Obscured",
        }
        try:
            self.skyCond_Desc = skyCond_dict[self.skyCond]
        except KeyError:
            self.skyCond_Desc = None

    def set_precipTI(self, precipTI):
        self.precipTI = precipTI

        precipTI_dict = {
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

        try:
            self.precipTI_Desc = precipTI_dict[self.precipTI]
        except KeyError:
            self.precipTI_Desc = None

    def set_airTempPres(self, airTempPres):
        self.airTempPres = airTempPres

    def set_windSpeed(self, windSpeed):
        self.windSpeed = windSpeed

        windSpeed_dict = {
            "C": "Calm",
            "L": "Light breeze",
            "M": "Moderate",
            "S": "Strong",
            "X": "gale force winds",
        }

        try:
            self.windSpeed_Desc = windSpeed_dict[self.windSpeed]
        except KeyError:
            self.windSpeed_Desc = None

    def set_windDir(self, windDir):
        self.windDir = windDir
