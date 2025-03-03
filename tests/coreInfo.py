class CoreInfo(object):
    """
    CoreInfo class for representing a "core Info" from a Snowpilot XML file
    """
    def __init__(self):
        self.pitID = None
        self.snowPitName = None
        self.date = None
        self.user = User()
        self.location = Location()
        self.weather = Weather()
        self.notes = None


class User(object):
    """
    User class for representing a Snow Pilot user
    """
    def __init__(self):
        self.operationID = None
        self.operationName = None
        self.professional = False # default to false
        self.contactPersonID = None
        self.username = None

    def __str__(self):
        user_str = ""
        user_str += f"OperationID: {self.operationID}\n"
        if self.operationName is not None:
            user_str += f"OperationName: {self.operationName}\n"
        user_str += f"Professional: {self.professional}\n"
        user_str += f"ContactPersonID: {self.contactPersonID}\n"
        user_str += f"Username: {self.username}\n"
        return user_str
    
    # Setters
    def set_operationID(self, operationID):
        self.operationID = operationID

    def set_operationName(self, operationName):
        self.operationName = operationName

    def set_professional(self, professional):
        self.professional = professional

    def set_contactPersonID(self, contactPersonID):
        self.contactPersonID = contactPersonID

    def set_username(self, username):
        self.username = username

class Location(object):
    """
    Location class for representing a location from a Snowpilot XML file
    """
    def __init__(self):
        self.latitude = None
        self.longitude = None

