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
print(f"Pit ID: {snowpit.coreInfo.pitID}")
print(f"Date: {snowpit.coreInfo.date}")
print(f"Location: {snowpit.coreInfo.location.latitude}, {snowpit.coreInfo.location.longitude}")

# Access snow profile data
print(f"HS: {snowpit.snowProfile.hS}")

# Access layer information
for i, layer in enumerate(snowpit.snowProfile.layers):
    print(f"Layer {i+1}: Depth {layer.depthTop}, Thickness {layer.thickness}")
    print(f"  Grain form: {layer.grainFormPrimary.grainForm}")
    print(f"  Hardness: {layer.hardness}")

# Access ECT test results
for ect in snowpit.stabilityTests.ECT:
    print(f"ECT at depth {ect.depthTop}: Score {ect.testScore}")
```

## Documentation

This documentation provides a comprehensive overview of the SnowPit object structure and how to access its various components. The nested structure allows for logical organization of the data while maintaining easy access to all information through dot notation.

For more detailed examples, the demos directory contains Jupyter notebooks demonstrating various use cases.

## SnowPit Object Structure

The SnowPit object is the main container for all snow pit data. It consists of four main components:

### 1. Core Info (snowpit.coreInfo)

Basic information about the snow pit:

- `pitID` - Unique identifier
- `pitName` - Name of the pit
- `date` - Date of observation
- `comment` - General comments
- `caamlVersion` - Version of CAAML schema used
- `user` - User information
- `location` - Location information
- `weatherConditions` - Weather conditions

Example:

```python
ID = snowpit.coreInfo.pitID
```

#### User Info (snowpit.coreInfo.user)

- `operationID` - ID of the operation
- `operationName` - Name of the operation
- `professional` - Boolean indicating if user is professional
- `userID` - User identifier
- `username` - SnowPilot username of the user

Example:

```python
operationID = snowpit.coreInfo.user.operationID
```

#### Location Info (snowpit.coreInfo.location)

- `latitude` - Decimal degrees
- `longitude` - Decimal degrees
- `elevation` - [value, units]
- `aspect` - Slope aspect
- `slopeAngle` - [value, units]
- `country` - Country name
- `region` - Region name
- `pitNearAvalanche` - Boolean
- `pitNearAvalancheLocation` - Location description if near avalanche

Example:

```python
lat = snowpit.coreInfo.location.latitude
```

#### Weather Conditions (snowpit.coreInfo.weatherConditions)

- `skyCond` - Sky conditions code
- `skyCond_Desc` - Sky conditions description
- `precipTI` - Precipitation type and intensity code
- `precipTI_Desc` - Precipitation description
- `airTempPres` - [temperature, units]
- `windSpeed` - Wind speed code
- `windSpeed_Desc` - Wind speed description
- `windDir` - Wind direction

Example:

```python
skyCond = snowpit.coreInfo.weatherConditions.skyCond
```

### 2. Snow Profile (snowpit.snowProfile)

Contains layer data and measurements:

#### Profile Info

- `measurementDirection` - Direction of measurements
- `profileDepth` - [depth, units]
- `hS` - Total snow height [value, units]

Example:

```python
measDir = snowpit.snowProfile.measurementDirection
```

#### Layers (snowpit.snowProfile.layers)

Example:

```python
layers_list = snowpit.snowProfile.layers
```

List of Layer objects, each containing:

- `depthTop` - [depth, units]
- `thickness` - [thickness, units]
- `hardness` - Hand hardness code
- `hardnessTop` - Top of layer hardness
- `hardnessBottom` - Bottom of layer hardness
- `wetness` - Wetness code
- `wetness_Desc` - Wetness description
- `layerOfConcern` - Boolean
- `grainFormPrimary` - grain form object representing primary grain form
- `grainFormSecondary` - grain form object representing secondary grain form

Example:

```python
depthTop_layer1 = snowpit.snowProfile.layers[0].depthTop
```

##### Grain Info (layer.grainFormPrimary or layer.grainFormSecondary)

- `grainForm` - Grain form code
- `grainSizeAvg` - [size, units]
- `grainSizeMax` - [size, units]
- `basicGrainClass_code` - Basic grain type code
- `basicGrainClass_name` - Basic grain type name
- `subGrainClass_code` - Detailed grain type code
- `subGrainClass_name` - Detailed grain type name

Example:

```python
primaryGrainForm_layer1 = snowpit.snowProfile.layers[0].grainFormPrimary.grainForm
```

#### Temperature Profile (snowpit.snowProfile.tempProfile)

List of temperature observations, each containing:

- `depth` - [depth, units]
- `snowTemp` - [temperature, units]

Example:

```python
depth_obs1 = snowpit.snowProfile.tempProfile[0].depth
```

#### Density Profile (snowpit.snowProfile.densityProfile)

List of density observation, each containing:

- `depthTop` - [depth, units]
- `thickness` - [thickness, units]
- `density` - [density, units]

Example:

```python
depthTop_obs1 = snowpit.snowProfile.densityProfile[0].depthTop
```

### 3. Stability Tests (snowpit.stabilityTests)

Contains lists of different stability test results:

- `ECT` - Extended Column Test
- `CT` - Compression Test
- `RBlock` - Rutschblock Test
- `PST` - Propagation Saw Test

Example:

```python
ECTs_list = snowpit.stabilityTests.ECT
```

#### Extended Column Test (snowpit.stabilityTests.ECT) is a list of ExtColumnTest objects

Each containing:

- `depthTop` - [depth, units]
- `testScore` - Test result code
- `propogation` - Boolean
- `numTaps` - Number of taps
- `comment` - Test comments

Example:

```python
ECT1_depthTop = snowpit.stabilityTests.ECT[0].depthTop
```

#### Compression Test (snowpit.stabilityTests.CT) is a list of ComprTest objects

Each containing:

- `depthTop` - [depth, units]
- `fractureCharacter` - Fracture character code
- `testScore` - Test result code
- `comment` - Test comments

Example:

```python
CT1_depthTop = snowpit.stabilityTests.CT[0].depthTop
```

#### Rutschblock Test (snowpit.stabilityTests.RBlock) is a list of RBlockTest objects

Each containing:

- `depthTop` - [depth, units]
- `fractureCharacter` - Fracture character code
- `releaseType` - Release type code
- `testScore` - Test result code
- `comment` - Test comments

Example:

```python
RBlock1_depthTop = snowpit.stabilityTests.RBlock[0].depthTop
```

#### Propagation Saw Test (snowpit.stabilityTests.PST) is a list of PropSawTest objects

Each containing:

- `depthTop` - [depth, units]
- `fractureProp` - Propagation result
- `cutLength` - [length, units]
- `columnLength` - [length, units]
- `comment` - Test comments

Example:

```python
PST1_depthTop = snowpit.stabilityTests.PST[0].depthTop
```

### 4. Whumpf Data (snowpit.whumpfData)

Custom SnowPilot data about collapsing weak layers:

- `whumpfCracking` - Presence of whumpf with cracking
- `whumpfNoCracking` - Presence of whumpf without cracking
- `crackingNoWhumpf` - Presence of cracking without whumpf
- `whumpfNearPit` - Whumpf location relative to pit
- `whumpfDepthWeakLayer` - Depth of weak layer
- `whumpfTriggeredRemoteAva` - If whumpf triggered remote avalanche
- `whumpfSize` - Size of the whumpf

Example:

```python
whumpfCracking = snowpit.whumpfData.whumpfCracking
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
        "PitID": pit.coreInfo.pitID,
        "Date": pit.coreInfo.date,
        "Location": f"{pit.coreInfo.location.latitude}, {pit.coreInfo.location.longitude}",
        "HS": pit.snowProfile.hS,
        "LayerCount": len(pit.snowProfile.layers),
        "ECTCount": len(pit.stabilityTests.ECT)
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
for ect in pit.stabilityTests.ECT:
    print(f"ECT at depth {ect.depthTop}: Score {ect.testScore}")
    print(f"  Propagation: {ect.propogation}")
    print(f"  Number of taps: {ect.numTaps}")
    print(f"  Comment: {ect.comment}")

# Find layers of concern
for layer in pit.snowProfile.layers:
    if layer.layerOfConcern:
        print(f"Layer of concern at depth {layer.depthTop}")
        print(f"  Grain form: {layer.grainFormPrimary.grainForm}")
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
