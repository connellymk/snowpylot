# SnowPylot

A Python library for working with CAAML.xml files containing snow pit data from [SnowPilot.org](https://snowpilot.org/).

## Features

- Parse CAAML.xml files from SnowPilot.org to access snow pit information including:
  - Core metadata (pit ID, date, location, etc.)
  - Snow profile data (layers, grain types, etc.)
  - Stability test results (ECT, CT, Rutschblock, PST)
  - Density Profile
  - Temperature Profile
  - Whumpf observations

## Installation

```bash
pip install snowpylot
```

Or clone the repository:

```bash
git clone https://github.com/connellymk/snowpylot.git
cd snowpylot
pip install -e .
```

## Quick Start

```python
from snowpylot import caaml_parser

# Parse a CAAML file
snowpit = caaml_parser("path/to/snowpit.caaml.xml")

# Access basic information
print(f"Pit ID: {snowpit.core_info.pit_id}")
print(f"Date: {snowpit.core_info.date}")
print(f"Location: {snowpit.core_info.location.latitude}, {snowpit.core_info.location.longitude}")

# Access snow profile data
print(f"HS: {snowpit.snow_profile.hs}")

# Access layer information
for i, layer in enumerate(snowpit.snow_profile.layers):
    print(f"Layer {i+1}: Depth {layer.depth_top}, Thickness {layer.thickness}")
    print(f"  Grain form: {layer.grain_form_primary.grain_form}")
    print(f"  Hardness: {layer.hardness}")

# Access ECT test results
for ect in snowpit.stability_tests.ECT:
    print(f"ECT at depth {ect.depth_top}: Score {ect.test_score}")
```

## Documentation

This documentation provides a comprehensive overview of the SnowPit object structure and how to access its various components. The nested structure allows for logical organization of the data while maintaining easy access to all information through dot notation.

For more detailed examples, the demos directory contains Jupyter notebooks demonstrating various use cases.

## SnowPit Object Structure

The SnowPit object is the main container for all snow pit data. It consists of four main components:

### 1. Core Info (snowpit.core_info)

Basic information about the snow pit:

- `pit_id` - Unique identifier
- `pit_name` - Name of the pit
- `date` - Date of observation
- `comment` - General comments
- `caaml_version` - Version of CAAML schema used
- `user` - User information
- `location` - Location information
- `weather_conditions` - Weather conditions

Example:

```python
ID = snowpit.core_info.pit_id
```

#### User Info (snowpit.core_info.user)

- `operation_id` - ID of the operation
- `operation_name` - Name of the operation
- `professional` - Boolean indicating if user is professional
- `user_id` - User identifier
- `username` - SnowPilot username of the user

Example:

```python
operationID = snowpit.core_info.user.operation_id
```

#### Location Info (snowpit.core_info.location)

- `latitude` - Decimal degrees
- `longitude` - Decimal degrees
- `elevation` - [value, units]
- `aspect` - Slope aspect
- `slope_angle` - [value, units]
- `country` - Country name
- `region` - Region name
- `pit_near_avalanche` - Boolean
- `pit_near_avalanche_location` - Location description if near avalanche

Example:

```python
lat = snowpit.core_info.location.latitude
```

#### Weather Conditions (snowpit.core_info.weather_conditions)

- `sky_cond` - Sky conditions code
- `sky_cond_desc` - Sky conditions description
- `precip_ti` - Precipitation type and intensity code
- `precip_ti_desc` - Precipitation description
- `air_temp_pres` - [temperature, units]
- `wind_speed` - Wind speed code
- `wind_speed_desc` - Wind speed description
- `wind_dir` - Wind direction

Example:

```python
skyCond = snowpit.core_info.weather_conditions.sky_cond
```

### 2. Snow Profile (snowpit.snow_profile)

Contains layer data and measurements:

#### Profile Info

- `measurement_direction` - Direction of measurements
- `profile_depth` - [depth, units]
- `hs` - Total snow height [value, units]

Example:

```python
measDir = snowpit.snow_profile.measurement_direction
```

#### Layers (snowpit.snow_profile.layers)

Example:

```python
layers_list = snowpit.snow_profile.layers
```

List of Layer objects, each containing:

- `depth_top` - [depth, units]
- `thickness` - [thickness, units]
- `hardness` - Hand hardness code
- `hardness_top` - Top of layer hardness
- `hardness_bottom` - Bottom of layer hardness
- `wetness` - Wetness code
- `wetness_desc` - Wetness description
- `layer_of_concern` - Boolean
- `grain_form_primary` - grain form object representing primary grain form
- `grain_form_secondary` - grain form object representing secondary grain form

Example:

```python
depthTop_layer1 = snowpit.snow_profile.layers[0].depth_top
```

##### Grain Info (layer.grain_form_primary or layer.grain_form_secondary)

- `grain_form` - Grain form code
- `grain_size_avg` - [size, units]
- `grain_size_max` - [size, units]
- `basic_grain_class_code` - Basic grain type code
- `basic_grain_class_name` - Basic grain type name
- `sub_grain_class_code` - Detailed grain type code
- `sub_grain_class_name` - Detailed grain type name

Example:

```python
primaryGrainForm_layer1 = snowpit.snow_profile.layers[0].grain_form_primary.grain_form
```

#### Temperature Profile (snowpit.snow_profile.temp_profile)

List of temperature observations, each containing:

- `depth` - [depth, units]
- `snow_temp` - [temperature, units]

Example:

```python
depth_obs1 = snowpit.snow_profile.temp_profile[0].depth
```

#### Density Profile (snowpit.snow_profile.density_profile)

List of density observation, each containing:

- `depth_top` - [depth, units]
- `thickness` - [thickness, units]
- `density` - [density, units]

Example:

```python
depthTop_obs1 = snowpit.snow_profile.density_profile[0].depth_top
```

### 3. Stability Tests (snowpit.stability_tests)

Contains lists of different stability test results:

- `ECT` - Extended Column Test
- `CT` - Compression Test
- `RBlock` - Rutschblock Test
- `PST` - Propagation Saw Test

Example:

```python
ECTs_list = snowpit.stability_tests.ECT
```

#### Extended Column Test (snowpit.stability_tests.ECT) is a list of ExtColumnTest objects

Each containing:

- `depth_top` - [depth, units]
- `test_score` - Test result code
- `propagation` - Boolean
- `num_taps` - Number of taps
- `comment` - Test comments

Example:

```python
ECT1_depthTop = snowpit.stability_tests.ECT[0].depth_top
```

#### Compression Test (snowpit.stability_tests.CT) is a list of ComprTest objects

Each containing:

- `depth_top` - [depth, units]
- `fracture_character` - Fracture character code
- `test_score` - Test result code
- `comment` - Test comments

Example:

```python
CT1_depthTop = snowpit.stability_tests.CT[0].depth_top
```

#### Rutschblock Test (snowpit.stability_tests.RBlock) is a list of RBlockTest objects

Each containing:

- `depth_top` - [depth, units]
- `fracture_character` - Fracture character code
- `release_type` - Release type code
- `test_score` - Test result code
- `comment` - Test comments

Example:

```python
RBlock1_depthTop = snowpit.stability_tests.RBlock[0].depth_top
```

#### Propagation Saw Test (snowpit.stability_tests.PST) is a list of PropSawTest objects

Each containing:

- `depth_top` - [depth, units]
- `fracture_prop` - Propagation result
- `cut_length` - [length, units]
- `column_length` - [length, units]
- `comment` - Test comments

Example:

```python
PST1_depthTop = snowpit.stability_tests.PST[0].depth_top
```

### 4. Whumpf Data (snowpit.whumpf_data)

Custom SnowPilot data about collapsing weak layers:

- `whumpf_cracking` - Presence of whumpf with cracking
- `whumpf_no_cracking` - Presence of whumpf without cracking
- `cracking_no_whumpf` - Presence of cracking without whumpf
- `whumpf_near_pit` - Whumpf location relative to pit
- `whumpf_depth_weak_layer` - Depth of weak layer
- `whumpf_triggered_remote_ava` - If whumpf triggered remote avalanche
- `whumpf_size` - Size of the whumpf

Example:

```python
whumpfCracking = snowpit.whumpf_data.whumpf_cracking
```

## Advanced Usage Examples

### Batch Processing Multiple Snow Pits

```python
import os
from snowpylot import caaml_parser

# Process all CAAML files in a directory
folder_path = "path/to/snowpits"
caaml_files = [f for f in os.listdir(folder_path) if f.endswith(".xml")]

results = []
for file in caaml_files:
    file_path = os.path.join(folder_path, file)
    pit = caaml_parser(file_path)

    # Extract data of interest
    result = {
        "PitID": pit.core_info.pit_id,
        "Date": pit.core_info.date,
        "Location": f"{pit.core_info.location.latitude}, {pit.core_info.location.longitude}",
        "HS": pit.snow_profile.hs,
        "LayerCount": len(pit.snow_profile.layers),
        "ECTCount": len(pit.stability_tests.ECT)
    }
    results.append(result)

# Convert to pandas DataFrame for analysis
import pandas as pd
df = pd.DataFrame(results)
print(df.head())
```

### Analyzing Stability Test Results

```python
from snowpylot import caaml_parser

pit = caaml_parser("path/to/snowpit.caaml.xml")

# Analyze ECT results
for ect in pit.stability_tests.ECT:
    print(f"ECT at depth {ect.depth_top}: Score {ect.test_score}")
    print(f"  Propagation: {ect.propagation}")
    print(f"  Number of taps: {ect.num_taps}")
    print(f"  Comment: {ect.comment}")

# Find layers of concern
for layer in pit.snow_profile.layers:
    if layer.layer_of_concern:
        print(f"Layer of concern at depth {layer.depth_top}")
        print(f"  Grain form: {layer.grain_form_primary.grain_form}")
        print(f"  Hardness: {layer.hardness}")
```

## Resources

- [SnowPilot.org](https://snowpilot.org/) - Source of snow pit data
- [Source Code for SnowPilot](https://github.com/SnowpitData/AvscienceServer)
- [CAAML Schema Documentation](http://caaml.org/Schemas/V4.2/Doc/) - CAAML data format specification
- [Snowpack Repository](https://github.com/ronimos/snowpack) - Tools built by Ron Simenhois to read and compare SNOWPACK.pro files and SnowPilot CAAML.xml files

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
