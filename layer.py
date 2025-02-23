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
        self.grainFormPrimary=Grain()
        self.grainFormSecondary=Grain()
        self.density=None
        self.wetness=None
        self.layerOfConcern=None
        self.comments=None

    def __str__(self):
        layer_str = ""
        layer_str += f"\n\t depthTop: {self.depthTop}"
        layer_str += f"\n\t thickness: {self.thickness}"
        layer_str += f"\n\t grainFormPrimary: {self.grainFormPrimary}"
        layer_str += f"\n\t grainFormSecondary: {self.grainFormSecondary}"
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
        self.grainForm = None
        self.grainSizeAvg = None
        self.grainSizeMax = None
        # Computed properties
        self.basicGrainClass_code = None
        self.basicGrainClass_name = None
        self.subGrainClass_code = None
        self.subGrainClass_name = None

    def __str__(self):
        grain_str = ""
        grain_str += f"\n\t\t grainForm: {self.grainForm}"
        grain_str += f"\n\t\t grainSizeAvg: {self.grainSizeAvg}"
        grain_str += f"\n\t\t grainSizeMax: {self.grainSizeMax}"
        grain_str += f"\n\t\t basicGrainClass_code: {self.basicGrainClass_code}"
        grain_str += f"\n\t\t basicGrainClass_name: {self.basicGrainClass_name}"
        grain_str += f"\n\t\t subGrainClass_code: {self.subGrainClass_code}"
        grain_str += f"\n\t\t subGrainClass_name: {self.subGrainClass_name}"
        return grain_str
    
    # Setters
    def set_grainForm(self, grainForm):
        self.grainForm = grainForm
        if len(grainForm) > 2:
            self.basicGrainClass_code = grainForm[:2]
            self.subGrainClass_code = grainForm[2:]
        else:
            self.basicGrainClass_code = grainForm

    def set_grainSizeAvg(self, grainSizeAvg):
        self.grainSizeAvg = grainSizeAvg

    def set_grainSizeMax(self, grainSizeMax):
        self.grainSizeMax = grainSizeMax

    def set_grainFormClass(self, grainFormClass):
        self.grainFormClass = grainFormClass
        
