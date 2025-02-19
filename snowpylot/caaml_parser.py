import xml.etree.ElementTree as ET
from .layer import Layer
from .snowPit import SnowPit
from .stabilityTests import *
from .snowProfile import SnowProfile, SurfaceCondition, TempMeasurement

def caaml_parser(file_path):
    '''
    The function receives a path to a SnowPilot caaml.xml file and returns a populated SnowPit object
    '''

    pit=SnowPit() # create a new SnowPit object
 
    # Parse file and add info to SnowPit object
    common_tag = '{http://caaml.org/Schemas/SnowProfileIACS/v6.0.3}' # Update to ready from xml file
    gml_tag = '{http://www.opengis.net/gml}'
    root = ET.parse(file_path).getroot()

    # caamlVersion
    pit.set_caamlVersion(common_tag)

    # pitID
    pitID_tag = common_tag + 'locRef'
    gml_id_tag = gml_tag + 'id'
    try:
        pitID_str = next(root.iter(pitID_tag), None).attrib[gml_id_tag]
        pitID = pitID_str.split('-')[-1]
    except AttributeError:
        pitID = None
    pit.set_pitID(pitID)

    # date
    dateTime_tag = common_tag + 'timePosition'
    try:
        dt = next(root.iter(dateTime_tag), None).text
    except AttributeError:
        dt = None
    date = dt.split('T')[0] if dt is not None else None
    pit.set_date(date)

    # User Information

    ## Location Information
    #Latitude and Longitude
    try:
        lat_long = next(root.iter(gml_tag + 'pos'), None).text
        lat_long=lat_long.split(' ')
    except AttributeError:
        lat_long = None


    if lat_long is not None:
        pit.location['Latitude'] = float(lat_long[0])
        pit.location['Longitude'] = float(lat_long[1])

    # Elevation, Aspect, and SlopeAngle: Reference code from Ron
    locations_params_tags = [common_tag + 'ElevationPosition', 
                                common_tag + 'AspectPosition', 
                                common_tag + 'SlopeAnglePosition']
    name_front_trim = len(common_tag)
    name_back_trim = -len('Position')
    position_params = [t for t in root.iter() if t.tag in locations_params_tags]
    for tp in position_params:
        pit.location[tp.tag[name_front_trim: name_back_trim]] = [tp.find(common_tag + 'position').text, tp.get('uom')]

    # Country and Region
    try:
        pit.location['Country'] = next(root.iter(common_tag + 'country'), None).text
    except AttributeError:
        pit.location['Country'] = None
    try:
        pit.location['Region'] = next(root.iter(common_tag + 'region'), None).text
    except AttributeError:
        pit.location['Region'] = None

    ## Snow Profile Information

    # Measurement Direction
    try:
        measurementDirection = next(root.iter(common_tag + 'SnowProfileMeasurements'), None).get('dir')
    except AttributeError:
        measurementDirection = None
    pit.snowProfile.set_measurementDirection(measurementDirection)

    # Profile Depth
    try:
        profileDepth = next(root.iter(common_tag + 'profileDepth'), None).text
        profileDepth_units = next(root.iter(common_tag + 'profileDepth'), None).get('uom')
        profileDepth = [float(profileDepth), profileDepth_units]
    except AttributeError:
        profileDepth = None
    pit.snowProfile.set_profileDepth(profileDepth)

    # hS
    try:
        hS_val = next(root.iter(common_tag + 'height'), None).text
        hS_units = next(root.iter(common_tag + 'height'), None).get('uom')
        hS = [float(hS_val), hS_units]
    except AttributeError:
        hS = None
    pit.snowProfile.set_hS(hS)

    ## Surface Conditions

    # Wind Loading

    # Boot Penetration
    try:
        penFoot_val = next(root.iter(common_tag + 'penetrationFoot'), None).text
        penFoot_units = next(root.iter(common_tag + 'penetrationFoot'), None).get('uom')
        penFoot = [float(penFoot_val), penFoot_units]
    except AttributeError:
        penFoot = None
    pit.snowProfile.surfCond.set_penetrationFoot(penFoot)

    # Ski Penetration
    try:
        penSki_val = next(root.iter(common_tag + 'penetrationSki'), None).text
        penSki_units = next(root.iter(common_tag + 'penetrationSki'), None).get('uom')
        penSki = [float(penSki_val), penSki_units]
    except AttributeError:
        penSki = None
    pit.snowProfile.surfCond.set_penetrationSki(penSki)
    
    # Layers
    layers = root.iter(common_tag + 'Layer')
    for layer in layers:
        layer_obj = Layer()
        for prop in layer.iter():
            if prop.tag.endswith('depthTop'):
                depthTop_val = prop.text
                depthTop_units = prop.get('uom')
                depthTop=[depthTop_val,depthTop_units]
                layer_obj.set_depthTop(depthTop)
            if prop.tag.endswith('thickness'):
                thickness_val = prop.text
                thickness_units = prop.get('uom')
                thickness=[thickness_val,thickness_units]
                layer_obj   .set_thickness(thickness)
            if prop.tag.endswith('grainFormPrimary'):
                grainFormPrimary = prop.text
                layer_obj.set_grainFormPrimary(grainFormPrimary)
            if prop.tag.endswith('hardness'):
                hardness = prop.text
                layer_obj.set_hardness(hardness)
            if prop.tag.endswith('wetness'):
                wetness = prop.text
                layer_obj.set_wetness(wetness)
            if prop.tag.endswith('layerOfConcern'):
                layerOfConcern = prop.text
                layer_obj.set_layerOfConcern(layerOfConcern)
        pit.snowProfile.add_layer(layer_obj)




    # Temperature Profile



    # Stability Tests
    test_results = next(root.iter(common_tag + 'stbTests'))

    for test in test_results.iter(common_tag + 'ExtColumnTest'): # All ECTs
        ect = ExtColumnTest()
        for prop in test[0].iter():
            if prop.tag.endswith('depthTop'):
                depthTop = float(prop.text)
                depthTop_units = prop.get('uom')
                ect.set_depthTop([depthTop, depthTop_units])
            elif prop.tag.endswith('testScore'):
                ect.set_testScore(prop.text)
            elif prop.tag.endswith('comment'):
                ect.set_comment(prop.text)

        pit.stabilityTests.add_ECT(ect)

    for test in test_results.iter(common_tag + 'ComprTest'): # All CTs
        ct = ComprTest()
        for prop in test[0].iter():
            if prop.tag.endswith('depthTop'):
                depthTop = float(prop.text)
                depthTop_units = prop.get('uom')
                ct.set_depthTop([depthTop, depthTop_units])
            elif prop.tag.endswith('testScore'):
                ct.set_testScore(prop.text)
            elif prop.tag.endswith('fractureCharacter'):
                ct.set_shearQuality(prop.text)
            elif prop.tag.endswith('comment'):
                ct.set_comment(prop.text)


        pit.stabilityTests.add_CT(ct)

    for test in test_results.iter(common_tag + 'RBlockTest'): # All RBTs  #### confirm correct tag
        rbt = RutschblockTest()
        for prop in test[0].iter():
            if prop.tag.endswith('depthTop'):
                depthTop = float(prop.text)
                depthTop_units = prop.get('uom')
                rbt.set_depthTop([depthTop, depthTop_units])
            elif prop.tag.endswith('testScore'):
                rbt.set_testScore(prop.text)
            elif prop.tag.endswith('fractureCharacter'):
                rbt.set_shearQuality(prop.text)
            elif prop.tag.endswith('releaseType'):
                rbt.set_releaseType(prop.text)
            elif prop.tag.endswith('comment'):
                rbt.set_comment(prop.text)

        pit.stabilityTests.add_RBT(rbt)

    for test in test_results.iter(common_tag + 'PropSawTest'): # All PSTs
        ps = PropSawTest()

        for prop in test[0].iter(): 
            if prop.tag.endswith('depthTop'):
                depthTop = float(prop.text)
                depthTop_units = prop.get('uom')
                ps.set_depthTop([depthTop, depthTop_units])
            elif prop.tag.endswith('fractureProp'):
                ps.set_fractureProp(prop.text)
            elif prop.tag.endswith('cutLength'):
                ps.set_cutLength(prop.text)
            elif prop.tag.endswith('columnLength'):
                ps.set_columnLength(prop.text)

        pit.stabilityTests.add_PST(ps)

    for test in test_results.iter(common_tag + 'StuffBlockTest'): # All SBTs
        sb = StuffBlockTest()
        for prop in test[0].iter():
            if prop.tag.endswith('depthTop'):
                depthTop = float(prop.text)
                depthTop_units = prop.get('uom')
                sb.set_depthTop([depthTop, depthTop_units])
            elif prop.tag.endswith('testScore'):
                sb.set_testScore(prop.text)
            elif prop.tag.endswith('fractureCharacter'):
                sb.set_shearQuality(prop.text)
            elif prop.tag.endswith('comment'):
                sb.set_comment(prop.text)

        pit.stabilityTests.add_SBT(sb)

    for test in test_results.iter(common_tag + 'ShovelShearTest'): # All SSTs
        ss = ShovelShearTest()
        for prop in test[0].iter():
            if prop.tag.endswith('depthTop'):
                depthTop = float(prop.text)
                depthTop_units = prop.get('uom')
                ss.set_depthTop([depthTop, depthTop_units])
            elif prop.tag.endswith('testScore'):
                ss.set_testScore(prop.text)
            elif prop.tag.endswith('comment'):
                ss.set_comment(prop.text)

        pit.stabilityTests.add_SST(ss)

    for test in test_results.iter(common_tag + 'DeepTapTest'): # All DTTs
        dt = DeepTapTest()
        for prop in test[0].iter():
            if prop.tag.endswith('depthTop'):
                depthTop = float(prop.text)
                depthTop_units = prop.get('uom')
                dt.set_depthTop([depthTop, depthTop_units])
            elif prop.tag.endswith('testScore'):
                dt.set_testScore(prop.text)
            elif prop.tag.endswith('fractureCharacter'):
                dt.set_shearQuality(prop.text)
            elif prop.tag.endswith('comment'):
                dt.set_comment(prop.text)

        pit.stabilityTests.add_DTT(dt)


    return pit



## Test
file_path = "snowpits_200_MT/snowpits-66387-caaml.xml"
pit1 = caaml_parser(file_path)
print("pit1")
print(pit1)



#file_path2 = "snowpits_200_MT/snowpits-66408-caaml.xml"
#pit2 = caaml_parser(file_path2)
#print("pit2")
#print(pit2)
