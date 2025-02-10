class Layer(object):

    """ 
    Layer class for representing a single layer in a snow pit  
    """

    def __init__(self,depthTop,thickness,grainFormPrimary,grainFormSecondary,hardness,wetness):
        self.depthTop=depthTop
        self.thickness=thickness
        self.grainFormPrimary=grainFormPrimary
        self.grainFormPrimary_grainClass = self.set_grainClass(self.grainFormPrimary)
        self.grainFormPrimary_grainSubClass=self.set_grainSubClass(self.grainFormPrimary)
        self.grainFormSecondary=grainFormSecondary
        self.hardness=hardness
        self.hardness_val=self.set_hardness_val(self.hardness)
        self.wetness=wetness


    def __str__(self):
        return f"Layer: {self.depthTop}, {self.thickness}, {self.grainFormPrimary}, {self.grainFormPrimary_grainClass}, {self.grainFormPrimary_grainSubClass}, {self.grainFormSecondary}, {self.hardness}, {self.wetness}"
    

    # Setter Functions
    def set_grainClass(self,grainForm):
        if grainForm is not None:
            return grainForm[:2]
        else:
            return None
    
    def set_grainSubClass(self,grainForm):
        if grainForm is not None and len(grainForm) > 2:
            return grainForm
        else:
            return None
    
    def set_hardness_val(self,hardness):
        if hardness is not None:
            hardness_dict = {
                'F-':1,'F':2,'F+':3,
                '4F-':2,'4F':2,'4F+':2,
                '1F-':3,'1F':3,'1F+':3,
                'P-':4,'P':4,'P+':4,
                'K-':5,'K':5,'K+':5,
                'I-':6,'I':6,'I+':6}
            return hardness_dict[hardness]
        else:
            return None

    # Getter Functions
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
    
    def get_grainFormPrimary_grainClass(self):
        return self.grainFormPrimary_grainClass
    
    def get_grainFormPrimary_grainSubClass(self):
        return self.grainFormPrimary_grainSubClass
    
    def get_hardness_val(self):
        return self.hardness_val
    

