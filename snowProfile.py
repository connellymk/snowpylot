from layer import Layer

class SnowProfile(object):

    """ 
    SnowProfile class for representing a snow profile from a SnowPilot caaml.xml file
    """

    def __init__(self):
        # Parsed properties
        self.measurementDirection = None
        self.profileDepth = None
        self.weatherConditions = None
        self.hS = None
        self.surfCond= None
        self.layers=[]
        self.tempProfile=None
        self.densityProfile=None
        # Computed properties
        self.layer_of_concern = None

    def __str__(self):
        snowProfile_str = ""
        snowProfile_str += f"\n    measurementDirection: {self.measurementDirection}"
        snowProfile_str += f"\n    profileDepth: {self.profileDepth}"
        snowProfile_str += f"\n    weatherConditions: {self.weatherConditions}"
        snowProfile_str += f"\n    hS: {self.hS}"
        snowProfile_str += f"\n    surfCond: {self.surfCond}"
        snowProfile_str += f"\n    Layers:"
        if self.layers is not None:
            for i, layer in enumerate(self.layers):
                snowProfile_str += f"\n    Layer {i+1}: {layer}"
        snowProfile_str += f"\n    tempProfile:"
        if self.tempProfile is not None:
            for i, temp in enumerate(self.tempProfile):
                snowProfile_str += f"\n    temp {i+1}: {temp}"
        snowProfile_str += f"\n    densityProfile:"
        if self.densityProfile is not None:
            for i, density in enumerate(self.densityProfile):
                snowProfile_str += f"\n    density {i+1}: {density}"
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

    def add_tempObs(self, tempObs):
        if self.tempProfile is None:
            self.tempProfile = []
        self.tempProfile.append(tempObs)

    def add_densityObs(self, densityObs):
        if self.densityProfile is None:
            self.densityProfile = []
        self.densityProfile.append(densityObs)

class WeatherConditions(object):

    """
    WeatherConditions class for representing the weather conditions of a snow profile from a SnowPilot caaml.xml file
    """

    def __init__(self):
        self.skyCond = None
        self.precipTI = None
        self.airTempPres = None
        self.windSpeed = None
        self.windDir = None

    def __str__(self):
        weatherConditions_str = ""
        weatherConditions_str += f"\n\t skyCond: {self.skyCond}"
        weatherConditions_str += f"\n\t precipTI: {self.precipTI}"
        weatherConditions_str += f"\n\t airTempPres: {self.airTempPres}"
        weatherConditions_str += f"\n\t windSpeed: {self.windSpeed}"
        weatherConditions_str += f"\n\t windDir: {self.windDir}"
        return weatherConditions_str
    
    # Setters
    def set_skyCond(self, skyCond):
        self.skyCond = skyCond

    def set_precipTI(self, precipTI):
        self.precipTI = precipTI

    def set_airTempPres(self, airTempPres):
        self.airTempPres = airTempPres

    def set_windSpeed(self, windSpeed):
        self.windSpeed = windSpeed

    def set_windDir(self, windDir):
        self.windDir = windDir

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

class TempObs(object):

    """
    TempMeasurement class for representing a temperature measurement from a SnowPilot caaml.xml file
    """
    
    def __init__(self):
        self.depth=None
        self.snowTemp=None
        

    def __str__(self):
        tempMeasurement_str = ""
        tempMeasurement_str += f"\n\t depth: {self.depth}"
        tempMeasurement_str += f"\n\t snowTemp: {self.snowTemp}"
        return tempMeasurement_str
    
    # Setters
    def set_depth(self, depth):
        self.depth = depth

    def set_snowTemp(self, snowTemp):
        self.snowTemp = snowTemp

class DensityObs(object):

    """
    DensityObs class for representing a density measurement from a SnowPilot caaml.xml file
    """
    
    def __init__(self):
        self.depthTop = None
        self.thickness = None
        self.density = None

    def __str__(self):
        densityObs_str = ""
        densityObs_str += f"\n\t depthTop: {self.depthTop}"
        densityObs_str += f"\n\t thickness: {self.thickness}"
        densityObs_str += f"\n\t density: {self.density}"
        return densityObs_str
    
    # Setters
    def set_depthTop(self, depthTop):
        self.depthTop = depthTop

    def set_thickness(self, thickness):
        self.thickness = thickness

    def set_density(self, density):
        self.density = density

