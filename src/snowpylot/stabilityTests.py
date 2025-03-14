class StabilityTests:
    """
    StabilityTests class for representing stability tests from a SnowPilot caaml.xml file

    Object holds a list of objects that represent stability tests
    """

    def __init__(self):
        self.ECT = []  # ExtColumn Test
        self.CT = []  # Compression Test
        self.RBlock = []  # Rutschblock Test
        self.PST = []  # Propogation Saw Test

    def __str__(self):
        stbTests_str = ""
        for i, test in enumerate(self.ECT):
            stbTests_str += f"\n    ExtColumnTest {i + 1}: {test}"
        for i, test in enumerate(self.CT):
            stbTests_str += f"\n    CompressionTest {i + 1}: {test}"
        for i, test in enumerate(self.RBlock):
            stbTests_str += f"\n    RutschblockTest {i + 1}: {test}"
        for i, test in enumerate(self.PST):
            stbTests_str += f"\n    PropSawTest {i + 1}: {test}"
        return stbTests_str

    def add_ECT(self, ect):
        self.ECT.append(ect)

    def add_CT(self, ct):
        self.CT.append(ct)

    def add_RBlock(self, rblock):
        self.RBlock.append(rblock)

    def add_PST(self, pst):
        self.PST.append(pst)


class ExtColumnTest:
    """
    ExtColumnTest class for representing results of ExtColumnTest stability test
    """

    def __init__(self):
        # Parsed Properties
        self.depthTop = None
        self.testScore = None
        self.comment = None
        # Computed Properties
        self.propogation = None
        self.numTaps = None

    def __str__(self):
        ect_str = ""
        ect_str += f"\n\t depthTop: {self.depthTop}"
        ect_str += f"\n\t testScore: {self.testScore}"
        ect_str += f"\n\t comment: {self.comment}"
        ect_str += f"\n\t propogation: {self.propogation}"
        ect_str += f"\n\t numTaps: {self.numTaps}"
        return ect_str

    def set_depthTop(self, depthTop):
        self.depthTop = depthTop

    def set_testScore(self, testScore):
        self.testScore = testScore

        propChar = testScore[3]
        if propChar == "P":
            self.propogation = True
        else:
            self.propogation = False

        numTaps = testScore[4:]
        self.numTaps = numTaps

    def set_comment(self, comment):
        self.comment = comment

    def set_propogation(self, propogation):
        self.propogation = propogation

    def set_numTaps(self, numTaps):
        self.numTaps = numTaps


class ComprTest:
    """
    ComprTest class for representing results of a Compression Test stability test
    """

    def __init__(self):
        self.depthTop = None
        self.fractureCharacter = None
        self.testScore = None
        self.comment = None

    def __str__(self):
        ct_str = ""
        ct_str += f"\n\t depthTop: {self.depthTop}"
        ct_str += f"\n\t fractureCharacter: {self.fractureCharacter}"
        ct_str += f"\n\t testScore: {self.testScore}"
        ct_str += f"\n\t comment: {self.comment}"
        return ct_str

    def set_depthTop(self, depthTop):
        self.depthTop = depthTop

    def set_fractureCharacter(self, fractureCharacter):
        self.fractureCharacter = fractureCharacter

    def set_testScore(self, testScore):
        self.testScore = testScore

    def set_comment(self, comment):
        self.comment = comment


class RBlockTest:
    """
    RBlockTest class for representing results of a Rutschblock Test
    """

    def __init__(self):
        self.depthTop = None
        self.fractureCharacter = None
        self.releaseType = None
        self.testScore = None
        self.comment = None

    def __str__(self):
        rbt_str = ""
        rbt_str += f"\n\t depthTop: {self.depthTop}"
        rbt_str += f"\n\t fractureCharacter: {self.fractureCharacter}"
        rbt_str += f"\n\t releaseType: {self.releaseType}"
        rbt_str += f"\n\t testScore: {self.testScore}"
        rbt_str += f"\n\t comment: {self.comment}"
        return rbt_str

    def set_depthTop(self, depthTop):
        self.depthTop = depthTop

    def set_fractureCharacter(self, fractureCharacter):
        self.fractureCharacter = fractureCharacter

    def set_releaseType(self, releaseType):
        self.releaseType = releaseType

    def set_testScore(self, testScore):
        self.testScore = testScore

    def set_comment(self, comment):
        self.comment = comment


class PropSawTest:
    """
    PropSawTest class for representing results of a Propogation Saw Test
    """

    def __init__(self):
        self.failure = None
        self.depthTop = None
        self.fractureProp = None
        self.cutLength = None
        self.columnLength = None
        self.comment = None

    def __str__(self):
        ps_str = ""
        ps_str += f"\n\t failure: {self.failure}"
        ps_str += f"\n\t depthTop: {self.depthTop}"
        ps_str += f"\n\t fractureProp: {self.fractureProp}"
        ps_str += f"\n\t cutLength: {self.cutLength}"
        ps_str += f"\n\t columnLength: {self.columnLength}"
        ps_str += f"\n\t comment: {self.comment}"
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
