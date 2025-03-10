from .snowProfile import SnowProfile
from .stabilityTests import StabilityTests
from .whumpfData import WhumpfData
from .coreInfo import CoreInfo


class SnowPit(object):
    """
    SnowPit class for representing a single snow pit  observation
    """

    def __init__(self):
        self.coreInfo = CoreInfo()  # Includes pitID, pitName, date, comment, caamlVersion, user, location, and weather
        self.snowProfile = (
            SnowProfile()
        )  # Includes layers, tempProfile, densityProfile, and surfCond
        self.stabilityTests = (
            StabilityTests()
        )  # Includes test results from stability tests
        self.whumpfData = WhumpfData()  # Includes custom SnowPilot "whumpfData"

    def __str__(self):
        snowPit_str = "SnowPit: "
        snowPit_str += f"\n Core Info: {self.coreInfo} "
        snowPit_str += f"\n Snow Profile: {self.snowProfile} "
        snowPit_str += f"\n Stability Tests: {self.stabilityTests} "
        snowPit_str += f"\n Whumpf Data: {self.whumpfData} "
        return snowPit_str

    # Setters

    def set_caamlVersion(self, caamlVersion):
        self.caamlVersion = caamlVersion

    def set_pitID(self, pitID):
        self.pitID = pitID

    def set_date(self, date):
        self.date = date

    def set_user(self, user):
        self.user = user

    def set_location(self, location):
        self.location = location

    def set_snowProfile(self, snowProfile):
        self.snowProfile = snowProfile

    def set_stabilityTests(self, stabilityTests):
        self.stabilityTests = stabilityTests

    # def set_whumpfData(self, whumpfData):
    #    self.whumpfData = whumpfData
