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
        layer_str += f"\n\t depthTop: {self.depthTop}"
        layer_str += f"\n\t thickness: {self.thickness}"
        layer_str += f"\n\t grainFormPrimary: {self.grainFormPrimary}"
        layer_str += f"\n\t hardness: {self.hardness}"
        layer_str += f"\n\t wetness: {self.wetness}"
        layer_str += f"\n\t layerOfConcern: {self.layerOfConcern}"
        layer_str += f"\n\t grainFormPrimary_Class: {self.grainFormPrimary_Class}"
        return layer_str
    

    # Setters
    def set_depthTop(self, depthTop):
        self.depthTop = depthTop

    def set_thickness(self, thickness):
        self.thickness = thickness

    def set_grainFormPrimary(self, grainFormPrimary):
        self.grainFormPrimary = grainFormPrimary
        self.grainFormPrimary_Class = self.set_grainForm_Class(grainFormPrimary)

    def set_hardness(self, hardness):
        self.hardness = hardness

    def set_wetness(self, wetness):
        self.wetness = wetness

    def set_layerOfConcern(self, layerOfConcern):
        self.layerOfConcern = layerOfConcern

    def set_grainForm_Class(self, grainForm):
        if len(grainForm) > 2:
            return grainForm[:2]
        else:
            return grainForm
