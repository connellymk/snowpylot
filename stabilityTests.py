class StabilityTests(object):

    """ 
    StabilityTests class for representing stability tests from a SnowPilot caaml.xml file

    Object holds a list of objects that represent stability tests
    """

    def __init__(self):
        self.conductedTests = [] # Initialize an empty list to store stability test results

    def __str__(self):
        stabilityTests_str = "StabilityTests: "
        for test in self.conductedTests:
            stabilityTests_str += f"\n {test}"
        return stabilityTests_str

    def add_test(self, test):
        self.conductedTests.append(test)


class ExtColumnTest(object):

    """
    ExtColumnTest class for representing results of ExtColumnTest stability test
    """

    def __init__(self):
        self.failure = None
        self.depthTop = None
        self.comment = None
        self.testScore = None



class ComprTest(object):

    """
    ComprTest class for representing results of a Compression Test stability test
    """

    def __init__(self):
        self.failure = None
        self.depthTop = None
        self.comment = None
        self.testScore = None
        self.fractureChar = None


class PropSawTest(object):

    """
    PropSawTest class for representing results of a Propogation Saw Test
    """

    def __init__(self):
        self.failure = None
        self.depthTop = None
        self.comment = None
        self.fractureProp = None
        self.cutLength = None

        self.columnLength = None


