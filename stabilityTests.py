class StabilityTests:

    """ 
    StabilityTests class for representing stability tests from a SnowPilot caaml.xml file

    Object holds a list of objects that represent stability tests
    """

    def __init__(self):
        self.conductedTests = [] # Initialize an empty list to store stability test results
        self.ECT = []
        self.CT = []
        self.PST = []


    def __str__(self):
        stbTests_str = ""
        for test in self.ECT:
            stbTests_str += f"\n {test}"
        for test in self.CT:
            stbTests_str += f"\n {test}"
        for test in self.PST:
            stbTests_str += f"\n {test}"
        return stbTests_str


    def add_test(self, test):
        self.conductedTests.append(test)


    def add_ECT(self, ect):
        self.ECT.append(ect)

    def add_CT(self, ct):
        self.CT.append(ct)

    def add_PST(self, pst):
        self.PST.append(pst)

class ExtColumnTest:

    """
    ExtColumnTest class for representing results of ExtColumnTest stability test
    """

    def __init__(self):
        self.failure = None
        self.depthTop = None
        self.comment = None
        self.testScore = None

    def __str__(self):
        ect_str = "ExtColumnTest: "
        ect_str += f"\n\t failure: {self.failure}"
        ect_str += f"\n\t depthTop: {self.depthTop}"
        ect_str += f"\n\t comment: {self.comment}"
        ect_str += f"\n\t testScore: {self.testScore}"
        return ect_str

    

    def set_failure(self, failure):
        self.failure = failure

    def set_depthTop(self, depthTop):
        self.depthTop = depthTop

    def set_comment(self, comment):
        self.comment = comment

    def set_testScore(self, testScore):
        self.testScore = testScore

class ComprTest:

    """
    ComprTest class for representing results of a Compression Test stability test
    """

    def __init__(self):
        self.failure = None
        self.depthTop = None
        self.comment = None
        self.testScore = None
        self.fractureChar = None

    def __str__(self):
        ct_str = "ComprTest: "
        ct_str += f"\n\t failure: {self.failure}"
        ct_str += f"\n\t depthTop: {self.depthTop}"
        ct_str += f"\n\t comment: {self.comment}"
        ct_str += f"\n\t testScore: {self.testScore}"
        ct_str += f"\n\t fractureChar: {self.fractureChar}"
        return ct_str


    def set_failure(self, failure):
        self.failure = failure

    def set_depthTop(self, depthTop):
        self.depthTop = depthTop

    def set_comment(self, comment):
        self.comment = comment

    def set_testScore(self, testScore):
        self.testScore = testScore

    def set_fractureChar(self, fractureChar):
        self.fractureChar = fractureChar


class PropSawTest:

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

    def __str__(self):
        ps_str = "PropSawTest: "
        ps_str += f"\n\t failure: {self.failure}"
        ps_str += f"\n\t depthTop: {self.depthTop}"
        ps_str += f"\n\t comment: {self.comment}"
        ps_str += f"\n\t fractureProp: {self.fractureProp}"
        ps_str += f"\n\t cutLength: {self.cutLength}"
        ps_str += f"\n\t columnLength: {self.columnLength}"
        return ps_str


    def set_failure(self, failure):
        self.failure = failure

    def set_depthTop(self, depthTop):
        self.depthTop = depthTop

    def set_comment(self, comment):
        self.comment = comment

    def set_fractureProp(self, fractureProp):
        self.fractureProp = fractureProp

    def set_cutLength(self, cutLength):
        self.cutLength = cutLength

    def set_columnLength(self, columnLength):
        self.columnLength = columnLength



