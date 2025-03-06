import xml.etree.ElementTree as ET
from layer import *
from snowPit import SnowPit
from stabilityTests import *
from snowProfile import *
from whumpfData import WumphData


def caaml_parser(file_path):
    """
    The function receives a path to a SnowPilot caaml.xml file and returns a populated SnowPit object
    """

    pit = SnowPit()  # create a new SnowPit object

    # Parse file and add info to SnowPit object
    common_tag = "{http://caaml.org/Schemas/SnowProfileIACS/v6.0.3}"  # Update to read from xml file
    gml_tag = "{http://www.opengis.net/gml}"
    snowpilot_tag = "{http://www.snowpilot.org/Schemas/caaml}"
    root = ET.parse(file_path).getroot()

    ### Core Info (pitID, pitName, date, user, location, weather, core comments, caamlVersion)

    # pitID
    try:
        pitID_str = next(root.iter(common_tag + "locRef"), None).attrib[gml_tag + "id"]
        pitID = pitID_str.split("-")[-1]
        pit.coreInfo.set_pitID(pitID)
    except AttributeError:
        pitID = None

    # snowPitName
    locRef = next(root.iter(common_tag + "locRef"), None)

    for prop in locRef.iter(common_tag + "name"):
        pitName = prop.text
        pit.coreInfo.set_pitName(pitName)

    # date
    for prop in root.iter(common_tag + "timePosition"):
        date = prop.text.split("T")[0] if prop.text is not None else None
        pit.coreInfo.set_date(date)

    # Comment
    metaData = next(root.iter(common_tag + "metaData"), None)

    for prop in metaData.iter(common_tag + "comment"):
        comment = prop.text
        pit.coreInfo.set_comment(comment)

    # caamlVersion
    pit.set_caamlVersion(common_tag)

    ## User (OperationID, OperationName, Professional, ContactPersonID, Username)
    srcRef = next(root.iter(common_tag + "srcRef"), None)

    # OperationID
    for prop in srcRef.iter(common_tag + "Operation"):
        operationID = prop.attrib[gml_tag + "id"]
        pit.coreInfo.user.set_operationID(operationID)
        pit.coreInfo.user.set_professional(
            True
        )  # If operation is present, then it is a professional operation

    # OperationName
    names = []
    for prop in srcRef.iter(common_tag + "Operation"):
        for subProp in prop.iter(common_tag + "name"):
            names.append(subProp.text)
    if names:
        pit.coreInfo.user.set_operationName(
            names[0]
        )  # Professional pits have operation name and contact name, the operation name is the first name
    else:
        pit.coreInfo.user.set_operationName(None)

    # ContactPersonID and Username
    for prop in srcRef.iter():
        if prop.tag.endswith(
            "Person"
        ):  # can handle "Person" (non-professional) or "ContactPerson" (professional)
            person = prop
            userID = person.attrib.get(gml_tag + "id")
            pit.coreInfo.user.set_userID(userID)
            for subProp in person.iter():
                if subProp.tag.endswith("name"):
                    pit.coreInfo.user.set_username(subProp.text)

    ## Location (latitude, longitude, elevation, aspect, slopeAngle, country, region, avalache proximity)

    # Latitude and Longitude
    try:
        lat_long = next(root.iter(gml_tag + "pos"), None).text
        lat_long = lat_long.split(" ")
        pit.coreInfo.location.set_latitude(float(lat_long[0]))
        pit.coreInfo.location.set_longitude(float(lat_long[1]))
    except AttributeError:
        lat_long = None

    # elevation
    for prop in locRef.iter(common_tag + "ElevationPosition"):
        uom = prop.attrib.get("uom")
        for subProp in prop.iter(common_tag + "position"):
            pit.coreInfo.location.set_elevation([round(float(subProp.text), 2), uom])

    # aspect
    for prop in locRef.iter(common_tag + "AspectPosition"):
        for subProp in prop.iter(common_tag + "position"):
            pit.coreInfo.location.set_aspect(subProp.text)

    # slopeAngle
    for prop in locRef.iter(common_tag + "SlopeAnglePosition"):
        uom = prop.attrib.get("uom")
        for subProp in prop.iter(common_tag + "position"):
            slopeAngle = subProp.text
            pit.coreInfo.location.set_slopeAngle([slopeAngle, uom])

    # country
    for prop in locRef.iter(common_tag + "country"):
        pit.coreInfo.location.set_country(prop.text)

    # region
    for prop in locRef.iter(common_tag + "region"):
        pit.coreInfo.location.set_region(prop.text)

    # proximity to avalanches
    for prop in root.iter(snowpilot_tag + "pitNearAvalanche"):
        if prop.text == "true":
            pit.coreInfo.location.set_pitNearAvalanche(True)
        try:
            location = prop.attrib.get("location")
            pit.coreInfo.location.set_pitNearAvalancheLocation(location)
        except AttributeError:
            location = None

    ## Weather Conditions (skyCond, precipTI, airTempPres, windSpeed, windDir)
    weatherCond = next(root.iter(common_tag + "weatherCond"), None)

    # skyCond
    for prop in weatherCond.iter(common_tag + "skyCond"):
        pit.coreInfo.weatherConditions.set_skyCond(prop.text)

    # precipTI
    for prop in weatherCond.iter(common_tag + "precipTI"):
        pit.coreInfo.weatherConditions.set_precipTI(prop.text)

    # airTempPres
    for prop in weatherCond.iter(common_tag + "airTempPres"):
        pit.coreInfo.weatherConditions.set_airTempPres(
            [round(float(prop.text), 2), prop.get("uom")]
        )

    # windSpeed
    for prop in weatherCond.iter(common_tag + "windSpd"):
        pit.coreInfo.weatherConditions.set_windSpeed(prop.text)

    # windDir
    for prop in weatherCond.iter(common_tag + "windDir"):
        for subProp in prop.iter(common_tag + "position"):
            pit.coreInfo.weatherConditions.set_windDir(subProp.text)

    ### Snow Profile (layers, tempProfile, densityProfile, surfCond)

    # layers
    stratProfile = next(root.iter(common_tag + "stratProfile"), None)
    layers = list(stratProfile)

    for layer in layers:
        layer_obj = Layer()

        for prop in layer.iter(common_tag + "depthTop"):
            layer_obj.set_depthTop([round(float(prop.text), 2), prop.get("uom")])

        for prop in layer.iter(common_tag + "thickness"):
            layer_obj.set_thickness([round(float(prop.text), 2), prop.get("uom")])

        for prop in layer.iter(common_tag + "hardness"):
            layer_obj.set_hardness(prop.text)

        for prop in layer.iter(common_tag + "hardnessTop"):
            layer_obj.set_hardnessTop(prop.text)

        for prop in layer.iter(common_tag + "hardnessBottom"):
            layer_obj.set_hardnessBottom(prop.text)

        for prop in layer.iter(common_tag + "grainFormPrimary"):
            layer_obj.grainFormPrimary = Grain()
            layer_obj.grainFormPrimary.set_grainForm(prop.text)

        for prop in layer.iter(common_tag + "grainFormSecondary"):
            layer_obj.grainFormSecondary = Grain()
            layer_obj.grainFormSecondary.set_grainForm(prop.text)

        for prop in layer.iter(common_tag + "grainSize"):
            uom = prop.get("uom")

            for subProp in prop.iter(common_tag + "avg"):
                layer_obj.grainFormPrimary.set_grainSizeAvg(
                    [round(float(subProp.text), 2), uom]
                )

            for subProp in prop.iter(common_tag + "avgMax"):
                layer_obj.grainFormPrimary.set_grainSizeMax(
                    [round(float(subProp.text), 2), uom]
                )

        for prop in layer.iter(common_tag + "wetness"):
            layer_obj.set_wetness(prop.text)

        for prop in layer.iter(common_tag + "layerOfConcern"):
            layer_obj.set_layerOfConcern(prop.text)

        for prop in layer.iter(common_tag + "comment"):
            layer_obj.set_comments(prop.text)

        pit.snowProfile.add_layer(layer_obj)

    # tempProfile
    tempProfile = next(root.iter(common_tag + "tempProfile"), None)
    if tempProfile is not None:  # Add check for None
        tempObs = [obs for obs in tempProfile if obs.tag.endswith("Obs")]
        for obs in tempObs:
            tempObs_obj = TempObs()
            for prop in obs.iter(common_tag + "depth"):
                print(f"Found depth: {prop.text}")  # Debug print
                tempObs_obj.set_depth([round(float(prop.text), 2), prop.get("uom")])
            for prop in obs.iter(common_tag + "snowTemp"):
                print(f"Found temp: {prop.text}")  # Debug print
                tempObs_obj.set_snowTemp([round(float(prop.text), 2), prop.get("uom")])
            pit.snowProfile.add_tempObs(tempObs_obj)
        print(
            f"Final number of temps in profile: {len(pit.snowProfile.tempProfile)}"
        )  # Debug print

    # densityProfile

    # surfCond

    ### Stability Tests (testResults)

    # testResults

    ### Wumph Data (wumphData)

    # wumphData

    return pit
