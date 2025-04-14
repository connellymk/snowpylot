import xml.etree.ElementTree as ET

from .layer import Grain, Layer
from .snow_pit import SnowPit
from .snow_profile import DensityObs, SurfaceCondition, TempObs
from .stability_tests import ComprTest, ExtColumnTest, PropSawTest, RBlockTest
from .whumpf_data import WhumpfData


def caaml_parser(file_path):
    """
    The function receives a path to a SnowPilot caaml.xml file, parses the file,
    and returns a populated SnowPit object
    """

    pit = SnowPit()  # create a new SnowPit object

    # tags in the caaml.xml file
    caaml_tag = (
        "{http://caaml.org/Schemas/SnowProfileIACS/v6.0.3}"  # TO DO: get from xml file
    )
    gml_tag = "{http://www.opengis.net/gml}"
    snowpilot_tag = "{http://www.snowpilot.org/Schemas/caaml}"

    root = ET.parse(file_path).getroot()

    ### Core Info:
    # (pit_id, pit_name, date, user, location, weather, core comments, caaml_version)
    loc_ref = next(root.iter(caaml_tag + "locRef"), None)

    # pit_id
    pit_id_str = loc_ref.attrib[gml_tag + "id"]
    pit_id = pit_id_str.split("-")[-1]
    pit.core_info.set_pit_id(pit_id)

    # snow_pit_name
    for prop in loc_ref.iter(caaml_tag + "name"):
        pit.core_info.set_pit_name(prop.text)

    # date
    for prop in root.iter(caaml_tag + "timePosition"):
        date = prop.text.split("T")[0] if prop.text is not None else None
        pit.core_info.set_date(date)

    # Comment
    meta_data = next(root.iter(caaml_tag + "metaData"), None)

    for prop in meta_data.iter(caaml_tag + "comment"):
        comment = prop.text
        pit.core_info.set_comment(comment)

    # caaml_version
    pit.core_info.set_caaml_version(caaml_tag)

    ## User (operation_id, operation_name, professional, contact_person_id, username)
    src_ref = next(root.iter(caaml_tag + "srcRef"), None)

    # operation_id
    for prop in src_ref.iter(caaml_tag + "Operation"):
        operation_id = prop.attrib[gml_tag + "id"]
        pit.core_info.user.set_operation_id(operation_id)
        pit.core_info.user.set_professional(
            True
        )  # If operation is present, then it is a professional operation

    # operation_name
    names = []
    for prop in src_ref.iter(caaml_tag + "Operation"):
        for sub_prop in prop.iter(caaml_tag + "name"):
            names.append(sub_prop.text)
    if names:
        pit.core_info.user.set_operation_name(
            names[0]
        )  # Professional pits have operation name and contact name,
        # the operation name is the first name
    else:
        pit.core_info.user.set_operation_name(None)

    # contact_person_id and username
    for prop in src_ref.iter():
        if prop.tag.endswith(
            "Person"
        ):  # can handle "Person" (non-professional) or "ContactPerson" (professional)
            person = prop
            user_id = person.attrib.get(gml_tag + "id")
            pit.core_info.user.set_user_id(user_id)
            for sub_prop in person.iter():
                if sub_prop.tag.endswith("name"):
                    pit.core_info.user.set_username(sub_prop.text)

    ## Location:
    # (latitude, longitude, elevation, aspect, slope_angle, country, region,
    # avalanche proximity)

    # Latitude and Longitude
    try:
        lat_long = next(root.iter(gml_tag + "pos"), None).text
        lat_long = lat_long.split(" ")
        pit.core_info.location.set_latitude(float(lat_long[0]))
        pit.core_info.location.set_longitude(float(lat_long[1]))
    except AttributeError:
        lat_long = None

    # elevation
    for prop in loc_ref.iter(caaml_tag + "ElevationPosition"):
        uom = prop.attrib.get("uom")
        for sub_prop in prop.iter(caaml_tag + "position"):
            pit.core_info.location.set_elevation([round(float(sub_prop.text), 2), uom])

    # aspect
    for prop in loc_ref.iter(caaml_tag + "AspectPosition"):
        for sub_prop in prop.iter(caaml_tag + "position"):
            pit.core_info.location.set_aspect(sub_prop.text)

    # slope_angle
    for prop in loc_ref.iter(caaml_tag + "SlopeAnglePosition"):
        uom = prop.attrib.get("uom")
        for sub_prop in prop.iter(caaml_tag + "position"):
            slope_angle = sub_prop.text
            pit.core_info.location.set_slope_angle([slope_angle, uom])

    # country
    for prop in loc_ref.iter(caaml_tag + "country"):
        pit.core_info.location.set_country(prop.text)

    # region
    for prop in loc_ref.iter(caaml_tag + "region"):
        pit.core_info.location.set_region(prop.text)

    # proximity to avalanches
    for prop in root.iter(snowpilot_tag + "pitNearAvalanche"):
        if prop.text == "true":
            pit.core_info.location.set_pit_near_avalanche(True)
        try:
            location = prop.attrib.get("location")
            pit.core_info.location.set_pit_near_avalanche_location(location)
        except AttributeError:
            location = None

    ## Weather Conditions:
    # (sky_cond, precip_ti, air_temp_pres, wind_speed, wind_dir)
    weather_cond = next(root.iter(caaml_tag + "weatherCond"), None)

    # sky_cond
    for prop in weather_cond.iter(caaml_tag + "skyCond"):
        pit.core_info.weather_conditions.set_sky_cond(prop.text)

    # precip_ti
    for prop in weather_cond.iter(caaml_tag + "precipTI"):
        pit.core_info.weather_conditions.set_precip_ti(prop.text)

    # air_temp_pres
    for prop in weather_cond.iter(caaml_tag + "airTempPres"):
        pit.core_info.weather_conditions.set_air_temp_pres(
            [round(float(prop.text), 2), prop.get("uom")]
        )

    # wind_speed
    for prop in weather_cond.iter(caaml_tag + "windSpd"):
        pit.core_info.weather_conditions.set_wind_speed(prop.text)

    # wind_dir
    for prop in weather_cond.iter(caaml_tag + "windDir"):
        for sub_prop in prop.iter(caaml_tag + "position"):
            pit.core_info.weather_conditions.set_wind_dir(sub_prop.text)

    ### Snow Profile:
    # (layers, temp_profile, density_profile, surf_cond)

    # Measurement Direction
    for prop in root.iter(caaml_tag + "SnowProfileMeasurements"):
        pit.snow_profile.set_measurement_direction(prop.get("dir"))

    # Profile Depth
    for prop in root.iter(caaml_tag + "profileDepth"):
        pit.snow_profile.set_profile_depth(
            [round(float(prop.text), 2), prop.get("uom")]
        )

    # hs
    for prop in root.iter(caaml_tag + "height"):
        pit.snow_profile.set_hs([round(float(prop.text), 2), prop.get("uom")])

    ## layers
    strat_profile = next(root.iter(caaml_tag + "stratProfile"), None)

    if strat_profile is not None:
        layers = [layer for layer in strat_profile if layer.tag.endswith("Layer")]

        for layer in layers:
            layer_obj = Layer()

            for prop in layer.iter(caaml_tag + "depthTop"):
                layer_obj.set_depth_top([round(float(prop.text), 2), prop.get("uom")])

            for prop in layer.iter(caaml_tag + "thickness"):
                layer_obj.set_thickness([round(float(prop.text), 2), prop.get("uom")])

            for prop in layer.iter(caaml_tag + "hardness"):
                layer_obj.set_hardness(prop.text)

            for prop in layer.iter(caaml_tag + "hardnessTop"):
                layer_obj.set_hardness_top(prop.text)

            for prop in layer.iter(caaml_tag + "hardnessBottom"):
                layer_obj.set_hardness_bottom(prop.text)

            for prop in layer.iter(caaml_tag + "grainFormPrimary"):
                layer_obj.grain_form_primary = Grain()
                layer_obj.grain_form_primary.set_grain_form(prop.text)

            for prop in layer.iter(caaml_tag + "grainFormSecondary"):
                layer_obj.grain_form_secondary = Grain()
                layer_obj.grain_form_secondary.set_grain_form(prop.text)

            for prop in layer.iter(caaml_tag + "grainSize"):
                uom = prop.get("uom")

                if layer_obj.grain_form_primary is None:
                    layer_obj.grain_form_primary = Grain()

                for sub_prop in prop.iter(caaml_tag + "avg"):
                    layer_obj.grain_form_primary.set_grain_size_avg(
                        [round(float(sub_prop.text), 2), uom]
                    )

                for sub_prop in prop.iter(caaml_tag + "avgMax"):
                    layer_obj.grain_form_primary.set_grain_size_max(
                        [round(float(sub_prop.text), 2), uom]
                    )

            for prop in layer.iter(caaml_tag + "wetness"):
                layer_obj.set_wetness(prop.text)

            for prop in layer.iter(caaml_tag + "layerOfConcern"):
                layer_obj.set_layer_of_concern(prop.text == "true")

            for prop in layer.iter(caaml_tag + "comment"):
                layer_obj.set_comments(prop.text)

            pit.snow_profile.add_layer(layer_obj)

    ## temp_profile
    temp_profile = next(root.iter(caaml_tag + "tempProfile"), None)

    if temp_profile is not None:
        temp_obs = [obs for obs in temp_profile if obs.tag.endswith("Obs")]

        for obs in temp_obs:
            temp_obs_obj = TempObs()

            for prop in obs.iter(caaml_tag + "depth"):
                temp_obs_obj.set_depth([round(float(prop.text), 2), prop.get("uom")])

            for prop in obs.iter(caaml_tag + "snowTemp"):
                temp_obs_obj.set_snow_temp(
                    [round(float(prop.text), 2), prop.get("uom")]
                )

            pit.snow_profile.add_temp_obs(temp_obs_obj)

    ## density_profile
    density_profile = next(root.iter(caaml_tag + "densityProfile"), None)

    if density_profile is not None:
        density_layer = [
            layer for layer in density_profile if layer.tag.endswith("Layer")
        ]

        for layer in density_layer:
            obs = DensityObs()
            for prop in layer.iter(caaml_tag + "depthTop"):
                obs.set_depth_top([round(float(prop.text), 2), prop.get("uom")])

            for prop in layer.iter(caaml_tag + "thickness"):
                obs.set_thickness([round(float(prop.text), 2), prop.get("uom")])

            for prop in layer.iter(caaml_tag + "density"):
                obs.set_density([round(float(prop.text), 2), prop.get("uom")])

            pit.snow_profile.add_density_obs(obs)

    ## surf_cond
    surf_cond = next(root.iter(caaml_tag + "surfCond"), None)

    if surf_cond is not None:
        pit.snow_profile.surf_cond = SurfaceCondition()

        # wind_loading
        for prop in surf_cond.iter(snowpilot_tag + "windLoading"):
            pit.snow_profile.surf_cond.set_wind_loading(prop.text)

        # penetration_foot
        for prop in surf_cond.iter(caaml_tag + "penetrationFoot"):
            pit.snow_profile.surf_cond.set_penetration_foot(
                [round(float(prop.text), 2), prop.get("uom")]
            )

        # penetration_ski
        for prop in surf_cond.iter(caaml_tag + "penetrationSki"):
            pit.snow_profile.surf_cond.set_penetration_ski(
                [round(float(prop.text), 2), prop.get("uom")]
            )

    ### Stability Tests (test_results)
    test_results = next(root.iter(caaml_tag + "stbTests"), None)

    if test_results is not None:
        ects = [test for test in test_results if test.tag.endswith("ExtColumnTest")]
        cts = [test for test in test_results if test.tag.endswith("ComprTest")]
        rblocks = [test for test in test_results if test.tag.endswith("RBlockTest")]
        psts = [test for test in test_results if test.tag.endswith("PropSawTest")]

        for ect in ects:
            ect_obj = ExtColumnTest()
            for prop in ect.iter(caaml_tag + "metaData"):
                for sub_prop in prop.iter(caaml_tag + "comment"):
                    ect_obj.set_comment(sub_prop.text)
            for prop in ect.iter(caaml_tag + "Layer"):
                for sub_prop in prop.iter(caaml_tag + "depthTop"):
                    ect_obj.set_depth_top([float(sub_prop.text), sub_prop.get("uom")])

            for prop in ect.iter(caaml_tag + "Results"):
                for sub_prop in prop.iter(caaml_tag + "testScore"):
                    ect_obj.set_test_score(sub_prop.text)

            pit.stability_tests.add_ect(ect_obj)

        for ct in cts:
            ct_obj = ComprTest()
            for prop in ct.iter(caaml_tag + "metaData"):
                for sub_prop in prop.iter(caaml_tag + "comment"):
                    ct_obj.set_comment(sub_prop.text)
            for prop in ct.iter(caaml_tag + "Layer"):
                for sub_prop in prop.iter(caaml_tag + "depthTop"):
                    ct_obj.set_depth_top([float(sub_prop.text), sub_prop.get("uom")])
            for prop in ct.iter(caaml_tag + "Results"):
                for sub_prop in prop.iter(caaml_tag + "fractureCharacter"):
                    ct_obj.set_fracture_character(sub_prop.text)
                for sub_prop in prop.iter(caaml_tag + "testScore"):
                    ct_obj.set_test_score(sub_prop.text)
            for _prop in ct.iter(caaml_tag + "noFailure"):
                ct_obj.set_test_score("CTN")

            pit.stability_tests.add_ct(ct_obj)

        for rblock in rblocks:
            rbt = RBlockTest()
            for prop in rblock.iter(caaml_tag + "metaData"):
                for sub_prop in prop.iter(caaml_tag + "comment"):
                    rbt.set_comment(sub_prop.text)
            for prop in rblock.iter(caaml_tag + "Layer"):
                for sub_prop in prop.iter(caaml_tag + "depthTop"):
                    rbt.set_depth_top([float(sub_prop.text), sub_prop.get("uom")])
            for prop in rblock.iter(caaml_tag + "Results"):
                for sub_prop in prop.iter(caaml_tag + "fractureCharacter"):
                    rbt.set_fracture_character(sub_prop.text)
                for sub_prop in prop.iter(caaml_tag + "releaseType"):
                    rbt.set_release_type(sub_prop.text)
                for sub_prop in prop.iter(caaml_tag + "testScore"):
                    rbt.set_test_score(sub_prop.text)

            pit.stability_tests.add_rblock(rbt)

        for pst in psts:
            pst_obj = PropSawTest()
            for prop in pst.iter(caaml_tag + "metaData"):
                for sub_prop in prop.iter(caaml_tag + "comment"):
                    pst_obj.set_comment(sub_prop.text)
            for prop in pst.iter(caaml_tag + "Layer"):
                for sub_prop in prop.iter(caaml_tag + "depthTop"):
                    pst_obj.set_depth_top([float(sub_prop.text), sub_prop.get("uom")])
            for prop in pst.iter(caaml_tag + "Results"):
                for sub_prop in prop.iter(caaml_tag + "fracturePropagation"):
                    pst_obj.set_fracture_prop(sub_prop.text)
                for sub_prop in prop.iter(caaml_tag + "cutLength"):
                    pst_obj.set_cut_length([float(sub_prop.text), sub_prop.get("uom")])
                for sub_prop in prop.iter(caaml_tag + "columnLength"):
                    pst_obj.set_column_length(
                        [float(sub_prop.text), sub_prop.get("uom")]
                    )

            pit.stability_tests.add_pst(pst_obj)

    ### Whumpf Data (whumpf_data)
    whumpf_data = next(root.iter(snowpilot_tag + "whumpfData"), None)

    if whumpf_data is not None:
        pit.whumpf_data = WhumpfData()

        for prop in whumpf_data.iter(snowpilot_tag + "whumpfCracking"):
            pit.whumpf_data.set_whumpf_cracking(prop.text)
        for prop in whumpf_data.iter(snowpilot_tag + "whumpfNoCracking"):
            pit.whumpf_data.set_whumpf_no_cracking(prop.text)
        for prop in whumpf_data.iter(snowpilot_tag + "crackingNoWhumpf"):
            pit.whumpf_data.set_cracking_no_whumpf(prop.text)
        for prop in whumpf_data.iter(snowpilot_tag + "whumpfNearPit"):
            pit.whumpf_data.set_whumpf_near_pit(prop.text)
        for prop in whumpf_data.iter(snowpilot_tag + "whumpfDepthWeakLayer"):
            pit.whumpf_data.set_whumpf_depth_weak_layer(prop.text)
        for prop in whumpf_data.iter(snowpilot_tag + "whumpfTriggeredRemoteAva"):
            pit.whumpf_data.set_whumpf_triggered_remote_ava(prop.text)
        for prop in whumpf_data.iter(snowpilot_tag + "whumpfSize"):
            pit.whumpf_data.set_whumpf_size(prop.text)
    else:
        pit.whumpf_data = None

    return pit
