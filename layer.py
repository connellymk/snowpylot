class Layer(object):

    """ 
    Layer class for representing a single layer in a snow pit  
    """

    def __init__(self, depthTop_uom, depthTop, thickness_uom, thickness, grainFormPrimary, grainFormSecondary, hardness, wetness):
        self.depthTop_uom=depthTop_uom
        self.depthTop=depthTop
        self.thickness_uom=thickness_uom
        self.thickness=thickness
        self.grainFormPrimary=grainFormPrimary
        self.grainFormSecondary=grainFormSecondary
        self.hardness=hardness
        self.wetness=wetness

