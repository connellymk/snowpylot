from xml.dom import minidom

class SnowPilot_object(object):

    """ 
    snowPilot_object class for representing a single snow pit from a snowPilot caaml.xml file
    """

    def __init__(self, file_path):
        self.file_path = file_path
        self.doc = self.parse_file(self.file_path)
        self.root = self.doc.documentElement

        self.metaData = self.set_metaData(self.doc)
        self.locationInfo = self.set_locationInfo(self.doc)
        self.pitInfo = self.set_pitInfo(self.doc)

    def parse_file(self, file_path):
        return minidom.parse(file_path)

    def set_metaData(self, doc):
        metaData_list = doc.getElementsByTagName('caaml:metaData')
        for child in metaData_list:
            for subchild in child.childNodes:
                print(subchild.nodeName)
                print(subchild.firstChild.nodeValue)
