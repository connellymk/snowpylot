class LocationInfo(object):

    """ 
    LocationInfo class for representing a the reported location of a snowPilot observation  
    """

    def __init__(self):
        self.elevation=None
        self.aspect=None
        self.slopeAngle=None
        self.latitude=None
        self.longitude=None
        self.country=None
        self.region=None


    #Setters
    def set_elevation(self, elevation):
        self.elevation = elevation

    def set_aspect(self, aspect):
        self.aspect = aspect    

    def set_slopeAngle(self, slopeAngle):
        self.slopeAngle = slopeAngle

    def set_latitude(self, latitude):
        self.latitude = latitude

    def set_longitude(self, longitude):
        self.longitude = longitude

    def set_country(self, country):
        self.country = country

    def set_region(self, region):
        self.region = region

    #Getters

    def get_elevation(self):
        return self.elevation
    
    def get_aspect(self):
        return self.aspect
    
    def get_slopeAngle(self):
        return self.slopeAngle
    
    def get_latitude(self):
        return self.latitude
    
    def get_longitude(self):
        return self.longitude
    
    def get_country(self):
        return self.country
    
    def get_region(self):
        return self.region


