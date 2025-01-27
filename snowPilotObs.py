from xml.dom import minidom
from locationInfo import LocationInfo
from user import User

class SnowPilot_object(object):

    """ 
    snowPilot_object class for representing a single snow pit from a snowPilot caaml.xml file
    """

    def __init__(self, file_path):
        self.file_path = file_path
        self.doc = self.parse_file(self.file_path)
        self.root = self.doc.documentElement


        self.date = self.set_date(self.doc, self.root)
        #self.user = self.set_user(self.doc, self.root)
        self.locationInfo = self.set_locationInfo(self.doc)
        #self.pitInfo = self.set_pitInfo(self.doc)

    def parse_file(self, file_path):
        return minidom.parse(file_path)
    
    #Setters

    def set_date(self, doc, root):

        timeRef_list = root.getElementsByTagName('caaml:dateTimeReport')
        dateTime=timeRef_list[0].firstChild.nodeValue
        dateTime=dateTime.split('T')

        print(dateTime)

        return dateTime[0]
    
    def set_locationInfo(self, doc, root):

        location=LocationInfo()
        
        # elevation
        elevation_list = root.getElementsByTagName('caaml:ElevationPosition')

        elevation=elevation_list[0].childNodes[1].firstChild.nodeValue if elevation_list[0].childNodes[1].firstChild else None
        elevation_unit=elevation_list[0].getAttribute('uom') if elevation_list[0].hasAttribute('uom') else None

        print(elevation)
        print(elevation_unit)




        # aspect

        # slope angle

        # latitude

        # longitude

        # country

        # region


    #Getters

    def get_date(self):
        return self.date


