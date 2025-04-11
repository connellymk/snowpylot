class Layer:
    """
    Layer class for representing a layer of snow from a SnowPilot caaml.xml file
    """

    def __init__(self):
        # Parsed properties
        self.depthTop = None
        self.thickness = None
        self.hardness = None
        self.hardnessTop = None
        self.hardnessBottom = None
        self.grainFormPrimary = None
        self.grainFormSecondary = None
        self.wetness = None
        self.layerOfConcern = False
        self.comments = None
        # Computed properties
        self.wetness_Desc = None

    def __str__(self):
        layer_str = ""
        layer_str += f"\n\t depthTop: {self.depthTop}"
        layer_str += f"\n\t thickness: {self.thickness}"
        layer_str += f"\n\t hardness: {self.hardness}"
        layer_str += f"\n\t hardnessTop: {self.hardnessTop}"
        layer_str += f"\n\t hardnessBottom: {self.hardnessBottom}"
        layer_str += f"\n\t grainFormPrimary: {self.grainFormPrimary}"
        layer_str += f"\n\t grainFormSecondary: {self.grainFormSecondary}"
        layer_str += f"\n\t wetness: {self.wetness}"
        layer_str += f"\n\t wetness_Desc: {self.wetness_Desc}"
        layer_str += f"\n\t layerOfConcern: {self.layerOfConcern}"
        layer_str += f"\n\t comments: {self.comments}"
        return layer_str

    # Setters
    def set_depthTop(self, depthTop):
        self.depthTop = depthTop

    def set_thickness(self, thickness):
        self.thickness = thickness

    def set_hardness(self, hardness):
        self.hardness = hardness

    def set_hardnessTop(self, hardnessTop):
        self.hardnessTop = hardnessTop

    def set_hardnessBottom(self, hardnessBottom):
        self.hardnessBottom = hardnessBottom

    def set_wetness(self, wetness):
        self.wetness = wetness

        wetness_dict = {
            "D": "Dry",
            "D-M": "Dry to moist",
            "M": "Moist",
            "M-W": "Moist to wet",
            "W": "Wet",
            "W-VW": "Wet to very wet",
            "VW": "Very wet",
            "VW-S": "Very wet to slush",
            "S": "Slush",
        }

        try:
            self.wetness_Desc = wetness_dict[self.wetness]
        except KeyError:
            self.wetness_Desc = None

    def set_layerOfConcern(self, layerOfConcern):
        self.layerOfConcern = layerOfConcern

    def set_comments(self, comments):
        self.comments = comments


class Grain:
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
        basicGrainClassDict = {
            "PP": "Precipitation particles",
            "DF": "Decomposing and fragmented precipitation particles",
            "RG": "Rounded grains",
            "FC": "Faceted crystals",
            "DH": "Depth hoar",
            "SH": "Surface hoar",
            "MF": "Melt forms",
            "IF": "Ice formations",
            "MM": "Machine made Snow",
        }
        subGrainClassDict = {
            "PPgp": "Graupel",
            "PPco": "Columns",
            "PPhl": "Hail",
            "PPpl": "Plates",
            "PPnd": "Needles",
            "PPsd": "Stellars, Dendrites",
            "PPir": "Irregular crystals",
            "PPip": "Ice pellets",
            "PPrm": "Rime",
            "DFdc": "Partly decomposed precipitation particles",
            "DFbk": "Wind-broken precipitation particles",
            "RGsr": "Small rounded particles",
            "RGlr": "Large rounded particles",
            "RGwp": "Wind packed",
            "RGxf": "Faceted rounded particles",
            "FCso": "Solid faceted particles",
            "FCsf": "Near surface faceted particles",
            "FCxr": "Rounding faceted particles",
            "DHcp": "Hollow cups",
            "DHpr": "Hollow prisms",
            "DHch": "Chains of depth hoar",
            "DHla": "Large striated crystals",
            "DHxr": "Rounding depth hoar",
            "SHsu": "Surface hoar crystals",
            "SHcv": "Cavity or crevasse hoar",
            "SHxr": "Rounding surface hoar",
            "MFcl": "Clustered rounded grains",
            "MFpc": "Rounded polycrystals",
            "MFsl": "Slush",
            "MFcr": "Melt-freeze crust",
            "IFil": "Ice layer",
            "IFic": "Ice column",
            "IFbi": "Basal ice",
            "IFrc": "Rain crust",
            "IFsc": "Sun crust",
            "MMrp": "Round polycrystalline particles",
            "MMci": "Crushed ice particles",
        }

        self.grainForm = grainForm
        if len(grainForm) > 2:
            self.basicGrainClass_code = grainForm[:2]
            self.subGrainClass_code = grainForm
            self.basicGrainClass_name = basicGrainClassDict[self.basicGrainClass_code]
            self.subGrainClass_name = subGrainClassDict[self.subGrainClass_code]
        else:
            self.basicGrainClass_code = grainForm
            self.basicGrainClass_name = basicGrainClassDict[self.basicGrainClass_code]

    def set_grainSizeAvg(self, grainSizeAvg):
        self.grainSizeAvg = grainSizeAvg

    def set_grainSizeMax(self, grainSizeMax):
        self.grainSizeMax = grainSizeMax

    def set_grainFormClass(self, grainFormClass):
        self.grainFormClass = grainFormClass
