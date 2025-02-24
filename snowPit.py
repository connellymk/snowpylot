from snowProfile import SnowProfile
from stabilityTests import StabilityTests
from whumpfData import WumphData

class SnowPit(object):

    """ 
    SnowPit class for representing a single snow pit  observation
    """

    def __init__(self):
        self.caamlVersion=None
        self.pitID = None 
        self.date = None 
        self.user = {
            'OperationID': None,
            'OperationName': None,
            'Professional': False,
            'ContactPersonID': None,
            'Username': None,
            }   
        self.location = {
            'Latitude': None, 
            'Longitude': None, 
            'Elevation': None, 
            'Aspect': None, 
            'SlopeAngle': None, 
            'Country': None, 
            'Region': None,
            'pitNearAvalanche': None} 
        self.snowProfile = SnowProfile() 
        self.stabilityTests = StabilityTests()
        self.wumphData = None
        

    def __str__(self):
        snowPit_str = "SnowPit: "
        snowPit_str += f"\n caamlVersion: {self.caamlVersion} "
        snowPit_str += f"\n pitID: {self.pitID} "
        snowPit_str += f"\n Date: {self.date} "
        snowPit_str += f"\n User:"
        for key, value in self.user.items():
            snowPit_str += f"\n    {key}: {value}"
        snowPit_str += f"\n Location:"
        for key, value in self.location.items():
            snowPit_str += f"\n    {key}: {value}"
        snowPit_str += f"\n Snow Profile: {self.snowProfile} "
        snowPit_str += f"\n Stability Tests: {self.stabilityTests} "
        snowPit_str += f"\n Wumph Data: {self.wumphData} "
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

    def set_wumphData(self, wumphData):
        self.wumphData = wumphData
