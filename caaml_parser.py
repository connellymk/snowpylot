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
    caaml_tag = "{http://caaml.org/Schemas/SnowProfileIACS/v6.0.3}"  # Update to read from xml file
    gml_tag = "{http://www.opengis.net/gml}"
    snowpilot_tag = "{http://www.snowpilot.org/Schemas/caaml}"
    root = ET.parse(file_path).getroot()

    ### Core Info (pitID, pitName, date, user, location, weather, core comments, caamlVersion)
    locRef = next(root.iter(caaml_tag + "locRef"), None)

    # pitID
    pitID_str = locRef.attrib[gml_tag + "id"]
    pitID = pitID_str.split("-")[-1]
    pit.coreInfo.set_pitID(pitID)

    # snowPitName
    for prop in locRef.iter(caaml_tag + "name"):
        pit.coreInfo.set_pitName(prop.text)

    # date
    for prop in root.iter(caaml_tag + "timePosition"):
        date = prop.text.split("T")[0] if prop.text is not None else None
        pit.coreInfo.set_date(date)

    # Comment
    metaData = next(root.iter(caaml_tag + "metaData"), None)

    for prop in metaData.iter(caaml_tag + "comment"):
        comment = prop.text
        pit.coreInfo.set_comment(comment)

    # caamlVersion
    pit.set_caamlVersion(caaml_tag)

    ## User (OperationID, OperationName, Professional, ContactPersonID, Username)
    srcRef = next(root.iter(caaml_tag + "srcRef"), None)

    # OperationID
    for prop in srcRef.iter(caaml_tag + "Operation"):
        operationID = prop.attrib[gml_tag + "id"]
        pit.coreInfo.user.set_operationID(operationID)
        pit.coreInfo.user.set_professional(
            True
        )  # If operation is present, then it is a professional operation

    # OperationName
    names = []
    for prop in srcRef.iter(caaml_tag + "Operation"):
        for subProp in prop.iter(caaml_tag + "name"):
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
    for prop in locRef.iter(caaml_tag + "ElevationPosition"):
        uom = prop.attrib.get("uom")
        for subProp in prop.iter(caaml_tag + "position"):
            pit.coreInfo.location.set_elevation([round(float(subProp.text), 2), uom])

    # aspect
    for prop in locRef.iter(caaml_tag + "AspectPosition"):
        for subProp in prop.iter(caaml_tag + "position"):
            pit.coreInfo.location.set_aspect(subProp.text)

    # slopeAngle
    for prop in locRef.iter(caaml_tag + "SlopeAnglePosition"):
        uom = prop.attrib.get("uom")
        for subProp in prop.iter(caaml_tag + "position"):
            slopeAngle = subProp.text
            pit.coreInfo.location.set_slopeAngle([slopeAngle, uom])

    # country
    for prop in locRef.iter(caaml_tag + "country"):
        pit.coreInfo.location.set_country(prop.text)

    # region
    for prop in locRef.iter(caaml_tag + "region"):
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
    weatherCond = next(root.iter(caaml_tag + "weatherCond"), None)

    # skyCond
    for prop in weatherCond.iter(caaml_tag + "skyCond"):
        pit.coreInfo.weatherConditions.set_skyCond(prop.text)

    # precipTI
    for prop in weatherCond.iter(caaml_tag + "precipTI"):
        pit.coreInfo.weatherConditions.set_precipTI(prop.text)

    # airTempPres
    for prop in weatherCond.iter(caaml_tag + "airTempPres"):
        pit.coreInfo.weatherConditions.set_airTempPres(
            [round(float(prop.text), 2), prop.get("uom")]
        )

    # windSpeed
    for prop in weatherCond.iter(caaml_tag + "windSpd"):
        pit.coreInfo.weatherConditions.set_windSpeed(prop.text)

    # windDir
    for prop in weatherCond.iter(caaml_tag + "windDir"):
        for subProp in prop.iter(caaml_tag + "position"):
            pit.coreInfo.weatherConditions.set_windDir(subProp.text)

    ### Snow Profile (layers, tempProfile, densityProfile, surfCond)

    ## layers
    stratProfile = next(root.iter(caaml_tag + "stratProfile"), None)

    if stratProfile is not None:
        layers = [layer for layer in stratProfile if layer.tag.endswith("Layer")]

        for layer in layers:
            layer_obj = Layer()

            for prop in layer.iter(caaml_tag + "depthTop"):
                layer_obj.set_depthTop([round(float(prop.text), 2), prop.get("uom")])

            for prop in layer.iter(caaml_tag + "thickness"):
                layer_obj.set_thickness([round(float(prop.text), 2), prop.get("uom")])

            for prop in layer.iter(caaml_tag + "hardness"):
                layer_obj.set_hardness(prop.text)

            for prop in layer.iter(caaml_tag + "hardnessTop"):
                layer_obj.set_hardnessTop(prop.text)

            for prop in layer.iter(caaml_tag + "hardnessBottom"):
                layer_obj.set_hardnessBottom(prop.text)

            for prop in layer.iter(caaml_tag + "grainFormPrimary"):
                layer_obj.grainFormPrimary = Grain()
                layer_obj.grainFormPrimary.set_grainForm(prop.text)

            for prop in layer.iter(caaml_tag + "grainFormSecondary"):
                layer_obj.grainFormSecondary = Grain()
                layer_obj.grainFormSecondary.set_grainForm(prop.text)

            for prop in layer.iter(caaml_tag + "grainSize"):
                uom = prop.get("uom")

                for subProp in prop.iter(caaml_tag + "avg"):
                    layer_obj.grainFormPrimary.set_grainSizeAvg(
                        [round(float(subProp.text), 2), uom]
                    )

                for subProp in prop.iter(caaml_tag + "avgMax"):
                    layer_obj.grainFormPrimary.set_grainSizeMax(
                        [round(float(subProp.text), 2), uom]
                    )

            for prop in layer.iter(caaml_tag + "wetness"):
                layer_obj.set_wetness(prop.text)

            for prop in layer.iter(caaml_tag + "layerOfConcern"):
                layer_obj.set_layerOfConcern(prop.text)

            for prop in layer.iter(caaml_tag + "comment"):
                layer_obj.set_comments(prop.text)

            pit.snowProfile.add_layer(layer_obj)

    ## tempProfile
    tempProfile = next(root.iter(caaml_tag + "tempProfile"), None)

    if tempProfile is not None:
        tempObs = [obs for obs in tempProfile if obs.tag.endswith("Obs")]

        for obs in tempObs:
            tempObs_obj = TempObs()

            for prop in obs.iter(caaml_tag + "depth"):
                tempObs_obj.set_depth([round(float(prop.text), 2), prop.get("uom")])

            for prop in obs.iter(caaml_tag + "snowTemp"):
                tempObs_obj.set_snowTemp([round(float(prop.text), 2), prop.get("uom")])

            pit.snowProfile.add_tempObs(tempObs_obj)

    ## densityProfile
    densityProfile = next(root.iter(caaml_tag + "densityProfile"), None)

    if densityProfile is not None:
        densityLayer = [
            layer for layer in densityProfile if layer.tag.endswith("Layer")
        ]

        for layer in densityLayer:
            obs = DensityObs()
            for prop in layer.iter(caaml_tag + "depthTop"):
                obs.set_depthTop([round(float(prop.text), 2), prop.get("uom")])

            for prop in layer.iter(caaml_tag + "thickness"):
                obs.set_thickness([round(float(prop.text), 2), prop.get("uom")])

            for prop in layer.iter(caaml_tag + "density"):
                obs.set_density([round(float(prop.text), 2), prop.get("uom")])

            pit.snowProfile.add_densityObs(obs)

    ## surfCond
    surfCond = next(root.iter(caaml_tag + "surfCond"), None)

    if surfCond is not None:
        pit.snowProfile.surfCond = SurfaceCondition()

        # windLoading
        for prop in surfCond.iter(snowpilot_tag + "windLoading"):
            pit.snowProfile.surfCond.set_windLoading(prop.text)

        # penetrationFoot
        for prop in surfCond.iter(caaml_tag + "penetrationFoot"):
            pit.snowProfile.surfCond.set_penetrationFoot(
                [round(float(prop.text), 2), prop.get("uom")]
            )

        # penetrationSki
        for prop in surfCond.iter(caaml_tag + "penetrationSki"):
            pit.snowProfile.surfCond.set_penetrationSki(
                [round(float(prop.text), 2), prop.get("uom")]
            )

    ### Stability Tests (testResults)

    # testResults

    ### Wumph Data (wumphData)

    # wumphData

    return pit
