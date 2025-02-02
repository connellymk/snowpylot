from xml.dom import minidom
from zz_location import LocationInfo
from zz_user import User

class SnowPilot_obs(object):

    """ 
    snowPilot_obs class for representing a single snow pit from a snowPilot caaml.xml file
    """

    def __init__(self, file_path):
        self.file_path = file_path
        self.doc = self.parse_file(self.file_path)
        self.root = self.doc.documentElement


        self.dateTime = self.set_dateTime(self.doc, self.root)
        #self.user = self.set_user(self.doc, self.root)
        self.locationInfo = self.set_locationInfo(self.doc, self.root)
        #self.pitInfo = self.set_pitInfo(self.doc)

    def parse_file(self, file_path):
        return minidom.parse(file_path)
    
    #Setters

    def set_dateTime(self, doc, root):

        timeRef_list = root.getElementsByTagName('caaml:dateTimeReport')
        dateTime=timeRef_list[0].firstChild.nodeValue
        dateTime=dateTime.split('T')

        return dateTime
    
    def set_locationInfo(self, doc, root):

        location=LocationInfo()
        
        # elevation
        elevation_list = root.getElementsByTagName('caaml:ElevationPosition')
        elevation_val=elevation_list[0].childNodes[1].firstChild.nodeValue if elevation_list[0].childNodes[1].firstChild else None
        elevation_unit=elevation_list[0].getAttribute('uom') if elevation_list[0].hasAttribute('uom') else None
        elevation = [elevation_val, elevation_unit]

        location.set_elevation(elevation)

        # aspect
        aspect_list = root.getElementsByTagName('caaml:AspectPosition')
        aspect=aspect_list[0].childNodes[1].firstChild.nodeValue if aspect_list[0].childNodes[1].firstChild else None

        location.set_aspect(aspect)

        # slope angle
        slopeAngle_list = root.getElementsByTagName('caaml:SlopeAnglePosition')
        slopeAngle_val=slopeAngle_list[0].childNodes[1].firstChild.nodeValue if slopeAngle_list[0].childNodes[1].firstChild else None
        slopeAngle_unit=slopeAngle_list[0].getAttribute('uom') if slopeAngle_list[0].hasAttribute('uom') else None
        slopeAngle=[slopeAngle_val, slopeAngle_unit]

        location.set_slopeAngle(slopeAngle)

        # Coords / latitude / longitude
        latLong_list = root.getElementsByTagName('caaml:pointLocation')
        lat_long=latLong_list[0].childNodes[1].childNodes[1].firstChild.nodeValue
        coords=lat_long
        lat_long=lat_long.split(' ')

        location.set_coords(coords)
        location.set_latitude(float(lat_long[0]))
        location.set_longitude(float(lat_long[1]))


        # country
        country_list = root.getElementsByTagName('caaml:country')
        country=country_list[0].firstChild.nodeValue

        location.set_country(country)

        # region
        region_list = root.getElementsByTagName('caaml:region')
        region=region_list[0].firstChild.nodeValue

        location.set_region(region)

        return location # Return the location object
    
    
    
    
    #Getters

    def get_date(self):
        return self.date


