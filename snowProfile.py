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

    def __str__(self):
        snowProfile_str = ""
        snowProfile_str += f"\n    measurementDirection: {self.measurementDirection}"
        snowProfile_str += f"\n    profileDepth: {self.profileDepth}"
        snowProfile_str += f"\n    hS: {self.hS}"
        snowProfile_str += f"\n    surfCond: {self.surfCond}"
        snowProfile_str += f"\n    layers:"
        for i, layer in enumerate(self.layers):
            snowProfile_str += f"\n\t layer {i+1}: {layer}"
        snowProfile_str += f"\n    tempProfile:"
        for i, temp in enumerate(self.tempProfile):
            snowProfile_str += f"\n\t temp {i+1}: {temp}"
        return snowProfile_str
    

    def set_measurementDirection(self, measurementDirection):
        self.measurementDirection = measurementDirection

    def set_profileDepth(self, profileDepth):
        self.profileDepth = profileDepth

    def set_hS(self, hS):
        self.hS = hS

    def set_surfCond(self, surfCond):
        self.surfCond = surfCond

    # Getters
    def get_measurementDirection(self):
        return self.measurementDirection

    def get_profileDepth(self):
        return self.profileDepth
    
    def get_hS(self):
        return self.hS

    def get_surfCond(self):
        return self.surfCond
        






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

    # Getters
    def get_windLoading(self):
        return self.windLoading
    
    def get_penetrationFoot(self):
        return self.penetrationFoot

    def get_penetrationSki(self):
        return self.penetrationSki
        
        


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
        layer_str += f"\n    depthTop: {self.depthTop}"
        layer_str += f"\n    thickness: {self.thickness}"
        layer_str += f"\n    grainFormPrimary: {self.grainFormPrimary}"
        layer_str += f"\n    hardness: {self.hardness}"
        layer_str += f"\n    wetness: {self.wetness}"
        layer_str += f"\n    layerOfConcern: {self.layerOfConcern}"
        layer_str += f"\n    grainFormPrimary_Class: {self.grainFormPrimary_Class}"
        return layer_str
    
    # Setters
    def set_depthTop(self, depthTop):
        self.depthTop = depthTop

    def set_thickness(self, thickness):
        self.thickness = thickness

    def set_grainFormPrimary(self, grainFormPrimary):
        self.grainFormPrimary = grainFormPrimary

    def set_hardness(self, hardness):
        self.hardness = hardness

    def set_wetness(self, wetness):
        self.wetness = wetness

    def set_layerOfConcern(self, layerOfConcern):
        self.layerOfConcern = layerOfConcern

    # Getters
    def get_depthTop(self):
        return self.depthTop
    
    def get_thickness(self):
        return self.thickness

    def get_grainFormPrimary(self):
        return self.grainFormPrimary
    
    def get_hardness(self):
        return self.hardness

    def get_wetness(self):
        return self.wetness

    def get_layerOfConcern(self):
        return self.layerOfConcern



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

    # Getters
    def get_depth(self):
        return self.depth

    def get_snowTemp(self):
        return self.snowTemp
        
        
        
        
