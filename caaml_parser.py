import xml.etree.ElementTree as ET
from snowPit import SnowPit
from stabilityTests import StabilityTests, ExtColumnTest, ComprTest, PropSawTest

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
    pit.set_pitId(pitID)

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
        coords = next(root.iter(gml_tag + 'pos'), None).text
        lat_long=coords.split(' ')
    except AttributeError:
        coords = None
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
    pit.location['Country'] = next(root.iter(common_tag + 'country'), None).text
    pit.location['Region'] = next(root.iter(common_tag + 'region'), None).text

    # Snow Profile Information

    # Stability Tests
    stbTests = StabilityTests()
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

        stbTests.add_ECT(ect)

    for test in test_results.iter(common_tag + 'ComprTest'): # All CTs
        ct = ComprTest()
        for prop in test[0].iter():
            if prop.tag.endswith('depthTop'):
                depthTop = float(prop.text)
                depthTop_units = prop.get('uom')
                ct.set_depthTop([depthTop, depthTop_units])
            elif prop.tag.endswith('testScore'):
                ct.set_testScore(prop.text)
            elif prop.tag.endswith('fractureChar'):
                ct.set_fractureChar(prop.text)

        stbTests.add_CT(ct)

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

        stbTests.add_PST(ps)

    pit.set_stabilityTests(stbTests)

    return pit


## Test


#file_path = "snowpits_200_MT/snowpits-66387-caaml.xml"
#pit1 = caaml_parser(file_path)
#print("pit1")
#print(pit1)


#file_path2 = "snowpits_200_MT/snowpits-66408-caaml.xml"
#pit2 = caaml_parser(file_path2)
#print("pit2")
#print(pit2)
