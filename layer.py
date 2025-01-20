class Layer(object):

    """ 
    Layer class for representing a single layer in a snow pit  
    """

    def __init__(self,depthTop,thickness,grainFormPrimary,grainFormSecondary,hardness,wetness):
        self.depthTop=depthTop
        self.thickness=thickness
        self.grainFormPrimary=grainFormPrimary
        self.grainFormSecondary=grainFormSecondary
        self.hardness=hardness
        self.wetness=wetness

    def __str__(self):
        return f"Layer: {self.depthTop}, {self.thickness}, {self.grainFormPrimary}, {self.grainFormSecondary}, {self.hardness}, {self.wetness}"
    def get_depthTop(self):
        return self.depthTop
    
    def get_thickness(self):
        return self.thickness
    
    def get_grainFormPrimary(self):
        return self.grainFormPrimary
    
    def get_grainFormSecondary(self):
        return self.grainFormSecondary
    
    def get_hardness(self):
        return self.hardness
    
    def get_wetness(self):
        return self.wetness