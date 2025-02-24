import xml.etree.ElementTree as ET
from layer import Layer, Grain
from snowPit import SnowPit
from stabilityTests import *
from snowProfile import SnowProfile, SurfaceCondition, WeatherConditions, TempObs, DensityObs
from whumpfData import WumphData

def caaml_parser(file_path):
    '''
    The function receives a path to a SnowPilot caaml.xml file and returns a populated SnowPit object
    '''

    pit=SnowPit() # create a new SnowPit object
 
    # Parse file and add info to SnowPit object
    common_tag = '{http://caaml.org/Schemas/SnowProfileIACS/v6.0.3}' # Update to ready from xml file
    gml_tag = '{http://www.opengis.net/gml}'
    snowpilot_tag = '{http://www.snowpilot.org/Schemas/caaml}'
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
    try:
        srcRef = next(root.iter(common_tag + 'srcRef'),None)
    except AttributeError:
        srcRef = None

    if srcRef is not None:
        for prop in srcRef.iter():
            if prop.tag.endswith('Person'):
                Person = prop
                pit.user['ContactPersonID'] = prop.attrib.get(gml_tag + 'id')
                for subProp in Person.iter():
                    if subProp.tag.endswith('name'):
                        pit.user['Username'] = subProp.text
            elif prop.tag.endswith('Operation'):
                Operation = prop
                pit.user['Professional'] = True
                pit.user['OperationID'] = prop.attrib.get(gml_tag + 'id')
                name = []
                for subProp in Operation.iter():
                    if subProp.tag.endswith('name'):
                        name.append(subProp.text)
                if len(name) > 0:
                    pit.user['OperationName'] = name[0]
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

    # pitNearAvalanche
    try:
        pitNearAvalanche_TF = next(root.iter(snowpilot_tag + 'pitNearAvalanche'), None).text
        pitNearAvalanche_loc = next(root.iter(snowpilot_tag + 'pitNearAvalanche'), None).get('location')
        pit.location['pitNearAvalanche'] = [pitNearAvalanche_TF, pitNearAvalanche_loc]
    except AttributeError:
        pit.location['pitNearAvalanche'] = None


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

    # Weather Conditions
    try:
        weatherConditions = next(root.iter(common_tag + 'weatherCond'), None)
    except AttributeError:
        weatherConditions = None

    if weatherConditions is not None:
        pit.snowProfile.weatherConditions = WeatherConditions()
        for prop in weatherConditions.iter():
            if prop.tag.endswith('skyCond'):
                pit.snowProfile.weatherConditions.set_skyCond(prop.text)
            if prop.tag.endswith('precipTI'):
                pit.snowProfile.weatherConditions.set_precipTI(prop.text)
            if prop.tag.endswith('airTempPres'):
                temp_val = prop.text
                temp_units = prop.get('uom')
                temp = [float(temp_val), temp_units]
                pit.snowProfile.weatherConditions.set_airTempPres(temp)
            if prop.tag.endswith('windSpd'):
                pit.snowProfile.weatherConditions.set_windSpeed(prop.text)
            if prop.tag.endswith('position'):
                pit.snowProfile.weatherConditions.set_windDir(prop.text)

    # hS
    try:
        hS_val = next(root.iter(common_tag + 'height'), None).text
        hS_units = next(root.iter(common_tag + 'height'), None).get('uom')
        hS = [float(hS_val), hS_units]
    except AttributeError:
        hS = None
    pit.snowProfile.set_hS(hS)

    ## Surface Conditions
    try:
        surfaceConditions = next(root.iter(common_tag + 'surfCond'), None)
    except AttributeError:
        surfaceConditions = None

    if surfaceConditions is not None:
        pit.snowProfile.surfCond = SurfaceCondition()

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
    stratProfile=next(root.iter(common_tag + 'stratProfile'),None)
    layers = list(stratProfile)

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
            if prop.tag.endswith('hardness'): 
                hardness = prop.text
                layer_obj.set_hardness(hardness)
            if prop.tag.endswith('hardnessTop'):
                hardnessTop = prop.text
                layer_obj.set_hardnessTop(hardnessTop)
            if prop.tag.endswith('hardnessBottom'):
                hardnessBottom = prop.text
                layer_obj.set_hardnessBottom(hardnessBottom)
            if prop.tag.endswith('grainFormPrimary'):
                layer_obj.grainFormPrimary = Grain()
                grainFormPrimary = prop.text
                layer_obj.grainFormPrimary.set_grainForm(grainFormPrimary)
            if prop.tag.endswith('grainSize'):
                grainSize_units = prop.get('uom')
                try:
                    grainSizeAvg = next(prop.iter(common_tag + 'avg'), None).text
                    layer_obj.grainFormPrimary.set_grainSizeAvg([float(grainSizeAvg), grainSize_units])
                except AttributeError:
                    grainSizeAvg = None
                try:
                    grainSizeMax = next(prop.iter(common_tag + 'avgMax'), None).text
                    layer_obj.grainFormPrimary.set_grainSizeMax([float(grainSizeMax), grainSize_units])
                except AttributeError:
                    grainSizeMax = None
            if prop.tag.endswith('grainFormSecondary'):
                layer_obj.grainFormSecondary = Grain()
                grainFormSecondary = prop.text
                if layer_obj.grainFormSecondary is not None:
                    layer_obj.grainFormSecondary.set_grainForm(grainFormSecondary)
            if prop.tag.endswith('density'):
                density = prop.text
                density_units = prop.get('uom')
                density = [float(density), density_units]
                layer_obj.set_density(density)
            if prop.tag.endswith('wetness'):
                wetness = prop.text
                layer_obj.set_wetness(wetness)
            if prop.tag.endswith('layerOfConcern'):
                layerOfConcern = prop.text
                layer_obj.set_layerOfConcern(layerOfConcern) 

        pit.snowProfile.add_layer(layer_obj)


    # Temperature Profile
    try:
        tempProfile = next(root.iter(common_tag + 'tempProfile'), None)
    except AttributeError:
        tempProfile = None

    if tempProfile is not None:
        for obs in tempProfile.iter(common_tag + 'Obs'):
            obs_obj = TempObs()
            for prop in obs.iter():
                if prop.tag.endswith('depth'):
                    depth_val = prop.text
                    depth_units = prop.get('uom')
                    obs_obj.set_depth([depth_val, depth_units])
                elif prop.tag.endswith('snowTemp'):
                    temp_val = prop.text
                    temp_units = prop.get('uom')
                    obs_obj.set_snowTemp([temp_val, temp_units])

            pit.snowProfile.add_tempObs(obs_obj)

    # Density Profile
    try:
        densityProfile = next(root.iter(common_tag + 'densityProfile'), None)
    except AttributeError:
        densityProfile = None

    if densityProfile is not None:
        for obs in densityProfile.iter(common_tag + 'Layer'):
            obs_obj = DensityObs()
            for prop in obs.iter():
                if prop.tag.endswith('depthTop'):
                    depthTop_val = prop.text
                    depthTop_units = prop.get('uom')
                    obs_obj.set_depthTop([depthTop_val, depthTop_units])
                elif prop.tag.endswith('thickness'):
                    thickness_val = prop.text
                    thickness_units = prop.get('uom')
                    obs_obj.set_thickness([thickness_val, thickness_units])
                elif prop.tag.endswith('density'):
                    density_val = prop.text
                    density_units = prop.get('uom')
                    obs_obj.set_density([density_val, density_units])

            pit.snowProfile.add_densityObs(obs_obj)




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

    # Custom Data (Whumpf Data and Wind Loading)
    try:
        customData = root.iter(common_tag+'customData')
    except AttributeError:
        customData = None

    for prop in customData:
        for sub_prop in prop:
            if(sub_prop.tag.endswith('whumpfData')):
                pit.wumphData = WumphData()
                whumpfData = sub_prop

            if(sub_prop.tag.endswith('windLoading')):
                pit.snowProfile.surfCond.windLoading = sub_prop.text

    if(pit.wumphData is not None):
        for prop in whumpfData:
            if(prop.tag.endswith('whumpfCracking')):
                pit.wumphData.set_wumphCracking(prop.text)
            if(prop.tag.endswith('whumpfNoCracking')):
                pit.wumphData.set_wumphNoCracking(prop.text)
            if(prop.tag.endswith('crackingNoWhumpf')):
                pit.wumphData.set_crackingNoWhumpf(prop.text)
            if(prop.tag.endswith('whumpfNearPit')):
                pit.wumphData.set_whumpfNearPit(prop.text)
            if(prop.tag.endswith('whumpfDepthWeakLayer')):
                pit.wumphData.set_whumpfDepthWeakLayer(prop.text)
            if(prop.tag.endswith('whumpfTriggeredRemoteAva')):
                pit.wumphData.set_whumpfTriggeredRemoteAva(prop.text)
            if(prop.tag.endswith('whumpfSize')):
                pit.wumphData.set_whumpfSize(prop.text)



    return pit



## Test
#file_path = "snowpits/snowpits_200_MT/snowpits-66387-caaml.xml"
#pit1 = caaml_parser(file_path)
#print("pit1")
#print(pit1)

#file_path2 = "snowpits/wumph_pits/snowpits-26875-caaml.xml"
#pit2 = caaml_parser(file_path2)
#print("pit2")
#print(pit2)

file_path3 = "snowpits/mkc_TESTPIT-23-Feb.caaml"
pit3 = caaml_parser(file_path3)
print("pit3")
print(pit3)

