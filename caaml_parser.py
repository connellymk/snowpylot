import xml.etree.ElementTree as ET

from snowPit import SnowPit


def caaml_parser(file_path):
 
    common_tag = '{http://caaml.org/Schemas/SnowProfileIACS/v6.0.3}'
    root = ET.parse(file_path).getroot()

    POS_LAT_LONG = '{http://www.opengis.net/gml}pos'
    locations_params_tags = [common_tag + 'ElevationPosition', 
                                 common_tag + 'AspectPosition', 
                                 common_tag + 'SlopeAnglePosition']
    name_front_trim = len(common_tag)
    name_back_trim = -len('Position')

    location = {}

    root = ET.parse(file_path).getroot()

    try: 
        loc = next(root.iter(POS_LAT_LONG), None).text
        location['lat'], location['long'] = map(float, loc.split(' '))
    except AttributeError:
        location = None
        return # No lat, lon loation for this pit
    
    position_params = [t for t in root.iter() if t.tag in locations_params_tags]
    print(position_params)
    for tp in position_params:
        print(tp.tag[name_front_trim: name_back_trim])
        location[tp.tag[name_front_trim: name_back_trim]] = tp.find(common_tag + 'position').text
    

    
    #print(location)

    pit=SnowPit() # create a new SnowPit object

    ## Parse into SnowPit object

    
    # pitID, date, dateTime

    # User Information

    # Location Information

    # Snow Profile Information

    # Stability Tests


    

    return pit


## Test

file_path = "snowpits_200_MT/snowpits-66387-caaml.xml"
pit1 = caaml_parser(file_path)
print(pit1)
