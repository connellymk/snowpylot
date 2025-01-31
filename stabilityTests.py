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


class extColumnTest(object):
    def __init__(self):
        self.extColumnTest = None

class comprTest(object):
    def __init__(self):
        self.comprTest = None

class propSawTest(object):
    def __init__(self):
        self.propSawTest = None


