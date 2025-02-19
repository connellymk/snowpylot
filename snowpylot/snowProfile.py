from .layer import Layer

class SnowProfile(object):

    """ 
    SnowProfile class for representing a snow profile from a SnowPilot caaml.xml file
    """

    def __init__(self):
        # Parsed properties
        self.measurementDirection = None
        self.profileDepth = None
        self.hS = None
        self.surfCond=SurfaceCondition()
        self.layers=[]
        self.tempProfile=[]
        # Computed properties
        self.layer_of_concern = None

    def __str__(self):
        snowProfile_str = ""
        snowProfile_str += f"\n    measurementDirection: {self.measurementDirection}"
        snowProfile_str += f"\n    profileDepth: {self.profileDepth}"
        snowProfile_str += f"\n    hS: {self.hS}"
        snowProfile_str += f"\n    surfCond: {self.surfCond}"
        snowProfile_str += f"\n    Layers:"
        for i, layer in enumerate(self.layers):
            snowProfile_str += f"\n    Layer {i+1}: {layer}"
        snowProfile_str += f"\n    tempProfile:"
        for i, temp in enumerate(self.tempProfile):
            snowProfile_str += f"\n    temp {i+1}: {temp}"
        snowProfile_str += f"\n    layer_of_concern: {self.layer_of_concern}"
        return snowProfile_str
    


    def set_measurementDirection(self, measurementDirection):
        self.measurementDirection = measurementDirection

    def set_profileDepth(self, profileDepth):
        self.profileDepth = profileDepth

    def set_hS(self, hS):
        self.hS = hS

    def set_surfCond(self, surfCond):
        self.surfCond = surfCond

    def add_layer(self, layer):
        self.layers.append(layer)
        if layer.layerOfConcern == True:
            self.layer_of_concern = layer



class SurfaceCondition(object):

    """
    SurfCond class for representing the surface condition of a snow profile from a SnowPilot caaml.xml file
    """
    
    def __init__(self):
        self.windLoading=None
        self.penetrationFoot=None
        self.penetrationSki=None
    
    def __str__(self):
        surfCond_str = ""
        surfCond_str += f"\n\t windLoading: {self.windLoading}"
        surfCond_str += f"\n\t penetrationFoot: {self.penetrationFoot}"
        surfCond_str += f"\n\t penetrationSki: {self.penetrationSki}"
        return surfCond_str
    

    # Setters
    def set_windLoading(self, windLoading):
        self.windLoading = windLoading

    def set_penetrationFoot(self, penetrationFoot):
        self.penetrationFoot = penetrationFoot

    def set_penetrationSki(self, penetrationSki):
        self.penetrationSki = penetrationSki


class TempMeasurement(object):

    """
    TempMeasurement class for representing a temperature measurement from a SnowPilot caaml.xml file
    """
    
    def __init__(self):
        self.depth=None
        self.snowTemp=None
        

    def __str__(self):
        tempMeasurement_str = ""
        tempMeasurement_str += f"\n    depth: {self.depth}"
        tempMeasurement_str += f"\n    snowTemp: {self.snowTemp}"
        return tempMeasurement_str
    
    # Setters
    def set_depth(self, depth):
        self.depth = depth

    def set_snowTemp(self, snowTemp):
        self.snowTemp = snowTemp

    