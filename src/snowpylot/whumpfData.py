class WhumpfData:
    """
    WhumpfData class for representing custom whumpf data
    """

    def __init__(self):
        self.whumpfCracking = None
        self.whumpfNoCracking = None
        self.crackingNoWhumpf = None
        self.whumpfNearPit = None
        self.whumpfDepthWeakLayer = None
        self.whumpfTriggeredRemoteAva = None
        self.whumpfSize = None

    def __str__(self):
        wumph_str = ""
        wumph_str += f"\n\t whumpfCracking: {self.whumpfCracking}"
        wumph_str += f"\n\t whumpfNoCracking: {self.whumpfNoCracking}"
        wumph_str += f"\n\t crackingNoWhumpf: {self.crackingNoWhumpf}"
        wumph_str += f"\n\t whumpfNearPit: {self.whumpfNearPit}"
        wumph_str += f"\n\t whumpfDepthWeakLayer: {self.whumpfDepthWeakLayer}"
        wumph_str += f"\n\t whumpfTriggeredRemoteAva: {self.whumpfTriggeredRemoteAva}"
        wumph_str += f"\n\t whumpfSize: {self.whumpfSize}"
        return wumph_str

    def set_whumpfCracking(self, whumpfCracking):
        self.whumpfCracking = whumpfCracking

    def set_whumpfNoCracking(self, whumpfNoCracking):
        self.whumpfNoCracking = whumpfNoCracking

    def set_crackingNoWhumpf(self, crackingNoWhumpf):
        self.crackingNoWhumpf = crackingNoWhumpf

    def set_whumpfNearPit(self, whumpfNearPit):
        self.whumpfNearPit = whumpfNearPit

    def set_whumpfDepthWeakLayer(self, whumpfDepthWeakLayer):
        self.whumpfDepthWeakLayer = whumpfDepthWeakLayer

    def set_whumpfTriggeredRemoteAva(self, whumpfTriggeredRemoteAva):
        self.whumpfTriggeredRemoteAva = whumpfTriggeredRemoteAva

    def set_whumpfSize(self, whumpfSize):
        self.whumpfSize = whumpfSize
