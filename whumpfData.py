class WumphData:
    """
    WumphData class for representing custom wumph data
    """

    def __init__(self):
        self.wumphCracking = None
        self.wumphNoCracking = None
        self.crackingNoWhumpf = None
        self.whumpfNearPit = None
        self.whumpfDepthWeakLayer = None
        self.whumpfTriggeredRemoteAva = None
        self.whumpfSize = None

    def __str__(self):
        wumph_str = ""
        wumph_str += f"\n\t wumphCracking: {self.wumphCracking}"
        wumph_str += f"\n\t wumphNoCracking: {self.wumphNoCracking}"
        wumph_str += f"\n\t crackingNoWhumpf: {self.crackingNoWhumpf}"
        wumph_str += f"\n\t whumpfNearPit: {self.whumpfNearPit}"
        wumph_str += f"\n\t whumpfDepthWeakLayer: {self.whumpfDepthWeakLayer}"
        wumph_str += f"\n\t whumpfTriggeredRemoteAva: {self.whumpfTriggeredRemoteAva}"
        wumph_str += f"\n\t whumpfSize: {self.whumpfSize}"
        return wumph_str

    def set_wumphCracking(self, wumphCracking):
        self.wumphCracking = wumphCracking

    def set_wumphNoCracking(self, wumphNoCracking):
        self.wumphNoCracking = wumphNoCracking

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
