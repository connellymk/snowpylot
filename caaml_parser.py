import xml.etree.ElementTree as ET
from snowPit import SnowPit

def caaml_parser(file_path):
    """
    Parses a SnowPilot caaml.xml file and returns a SnowPit object
    """

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

    # Location Information

    # Snow Profile Information

    # Stability Tests

    return pit


## Test

file_path = "snowpits_200_MT/snowpits-66387-caaml.xml"
pit1 = caaml_parser(file_path)
print(pit1)
