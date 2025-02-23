class Layer(object):

    """
    Layer class for representing a layer of snow from a SnowPilot caaml.xml file
    """
    
    def __init__(self):
        # Parsed properties
        self.depthTop=None
        self.thickness=None
        self.hardness1=None
        self.hardness2=None
        self.grainTypePrimary=Grain()
        self.grainTypeSecondary=Grain()
        self.density=None
        self.wetness=None
        self.layerOfConcern=None
        self.comments=None

    def __str__(self):
        layer_str = ""
        layer_str += f"\n\t depthTop: {self.depthTop}"
        layer_str += f"\n\t thickness: {self.thickness}"
        layer_str += f"\n\t grainTypePrimary: {self.grainTypePrimary}"
        layer_str += f"\n\t grainTypeSecondary: {self.grainTypeSecondary}"
        layer_str += f"\n\t density: {self.density}"
        layer_str += f"\n\t wetness: {self.wetness}"
        layer_str += f"\n\t layerOfConcern: {self.layerOfConcern}"
        layer_str += f"\n\t comments: {self.comments}"
        return layer_str
    

    # Setters
    def set_depthTop(self, depthTop):
        self.depthTop = depthTop

    def set_thickness(self, thickness):
        self.thickness = thickness

    def set_grainTypePrimary(self, grainTypePrimary):
        self.grainTypePrimary = grainTypePrimary

    def set_grainTypeSecondary(self, grainTypeSecondary):
        self.grainTypeSecondary = grainTypeSecondary

    def set_hardness1(self, hardness1):
        self.hardness1 = hardness1

    def set_hardness2(self, hardness2):
        self.hardness2 = hardness2

    def set_wetness(self, wetness):
        self.wetness = wetness

    def set_layerOfConcern(self, layerOfConcern):
        self.layerOfConcern = layerOfConcern

    def set_comments(self, comments):
        self.comments = comments

        

class Grain(object):

    def __init__(self):
        # Parsed properties
        self.grainType = None
        self.grainSizeAvg = None
        self.grainSizeMax = None
        # Computed properties
        self.basicGrainClass = None
        self.subGrainClass = None
        

    def __str__(self):
        grain_str = ""
        grain_str += f"\n\t grainType: {self.grainType}"
        grain_str += f"\n\t grainSizeAvg: {self.grainSizeAvg}"
        grain_str += f"\n\t grainSizeMax: {self.grainSizeMax}"
        return grain_str
    
    # Setters
    def set_grainType(self, grainType):
        self.grainType = grainType
        if len(grainType) > 2:
            self.basicGrainClass = grainType[:2]
            self.subGrainClass = grainType
        else:
            self.basicGrainClass = grainType

    def set_grainSizeAvg(self, grainSizeAvg):
        self.grainSizeAvg = grainSizeAvg

    def set_grainSizeMax(self, grainSizeMax):
        self.grainSizeMax = grainSizeMax

    def set_grainFormClass(self, grainFormClass):
        self.grainFormClass = grainFormClass
        
