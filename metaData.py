class MetaData(object):

    """ 
    metaData object class for representing the meta data from a snowPilot caaml.xml file
    """

    def __init__(self):
        self.comment = None
        self.date = None
        self.time = None
        self.user = None

    def set_comment(self, comment):
        self.comment = comment

    def set_date(self, date):
        self.date = date

    def set_time(self, time):
        self.time = time    

    def set_user(self, user):
        self.user = user

    def get_comment(self):
        return self.comment

    def get_date(self):
        return self.date

    def get_time(self):
        return self.time


