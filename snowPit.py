from location import Location
from snowProfile import SnowProfile
from user import User
from stabilityTests import StabilityTests

class SnowPit(object):

    """ 
    SnowPit class for representing a single snow pit  observation from a SnowPilot caaml.xml file
    """

    def __init__(self):
        self.pitId = None 
        self.date = None 
        self.dateTime = None 
        self.user = User()  
        self.location = Location()   
        self.snowProfile = SnowProfile() 
        self.stabilityTests = StabilityTests()
        self.caamlVersion=None

    def __str__(self):
        snowPit_str = "SnowPit: "
        snowPit_str += f"\n pitId: {self.pitId} "
        snowPit_str += f"\n date: {self.date} "
        snowPit_str += f"\n dateTime: {self.dateTime} "
        snowPit_str += f"\n user: {self.user} "
        snowPit_str += f"\n location: {self.location} "
        snowPit_str += f"\n snowProfile: {self.snowProfile} "
        snowPit_str += f"\n extColumnTest: {self.extColumnTest} "
        snowPit_str += f"\n propSawTest: {self.propSawTest} "
        snowPit_str += f"\n caamlVersion: {self.caamlVersion} "
        return snowPit_str


    # Setters
    def set_pitId(self, pitId):
        self.pitId = pitId

    def set_date(self, date):
        self.date = date

    def set_dateTime(self, dateTime):
        self.dateTime = dateTime

    def set_user(self, user):
        self.user = user

    def set_location(self, location):
        self.location = location

    def set_snowProfile(self, snowProfile):
        self.snowProfile = snowProfile

    def set_extColumnTest(self, extColumnTest):
        self.extColumnTest = extColumnTest

    def set_comprTest(self, comprTest):
        self.comprTest = comprTest

    def set_propSawTest(self, propSawTest):
        self.propSawTest = propSawTest  

    def set_caamlVersion(self, caamlVersion):
        self.caamlVersion = caamlVersion    

    # Getters
    def get_pitId(self):
        return self.pitId 
    
    def get_date(self):
        return self.date
    
    def get_dateTime(self):
        return self.dateTime
    
    def get_user(self):
        return self.user
    
    def get_location(self):
        return self.location
    
    def get_snowProfile(self):
        return self.snowProfile
    
    def get_extColumnTest(self):
        return self.extColumnTest
    
    def get_comprTest(self):
        return self.comprTest
    
    def get_propSawTest(self):
        return self.propSawTest
    
    def get_caamlVersion(self):
        return self.caamlVersion


