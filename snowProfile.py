class SnowProfile(object):

    """ 
    SnowProfile class for representing a snow profile from a SnowPilot caaml.xml file
    """

    def __init__(self):
        self.measurementDirection = None
        self.profileDepth = None
        self.hS = None
        self.surfCond=SurfaceCondition()
        self.layers=[]
        self.tempProfile=[]

class SurfaceCondition(object):

    """
    SurfCond class for representing the surface condition of a snow profile from a SnowPilot caaml.xml file
    """
    
    def __init__(self):
        self.windLoading=None
        self.penetrationFoot=None
        self.penetrationSki=None
    
    def __str__(self):
        surfCond_str = "Surface Conditions: "
        surfCond_str += f"\n\    windLoading: {self.windLoading}"
        surfCond_str += f"\n\    penetrationFoot: {self.penetrationFoot}"
        surfCond_str += f"\n\    penetrationSki: {self.penetrationSki}"
        return surfCond_str

class Layer(object):

    """
    Layer class for representing a layer of snow from a SnowPilot caaml.xml file
    """
    
    def __init__(self):
        # Parsed properties
        self.depthTop=None
        self.thickness=None
        self.grainFormPrimary=None
        self.hardness=None
        self.wetness=None
        self.layerOfConcern=None
        # Computed properties
        self.grainFormPrimary_Class=None

    def __str__(self):
        layer_str = ""
        layer_str += f"\n\    depthTop: {self.depthTop}"
        layer_str += f"\n\    thickness: {self.thickness}"
        layer_str += f"\n\    grainFormPrimary: {self.grainFormPrimary}"
        layer_str += f"\n\    hardness: {self.hardness}"
        layer_str += f"\n\    wetness: {self.wetness}"
        layer_str += f"\n\    layerOfConcern: {self.layerOfConcern}"
        layer_str += f"\n\    grainFormPrimary_Class: {self.grainFormPrimary_Class}"
        return layer_str


class TempMeasurement(object):

    """
    TempMeasurement class for representing a temperature measurement from a SnowPilot caaml.xml file
    """
    
    def __init__(self):
        self.depth=None
        self.snowTemp=None
        
