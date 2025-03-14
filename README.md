# SnowPylot

A Python library for working with CAAML snow profile data from SnowPilot.org.

## Features

- Parse CAAML.xml files from SnowPilot.org
- Access information about the snow pit (pit ID, date, location, snow profile, stability test results, etc.)
- Work with snow layers and grain types
- Access stability test results
- Handle whumpf observations


## Installation

```bash
pip install snowpylot
```

for clone the repo:

```bash
git clone https://github.com/connellymk/snowpylot.git
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.



## Usage

```python
from snowpylot import caaml_parser

# Parse a CAAML file
snowpit = caaml_parser("path/to/snowpit.caaml.xml")

```

This documentation provides a comprehensive overview of the SnowPit object structure and how to access its various components. The nested structure allows for logical organization of the data while maintaining easy access to all information through dot notation.

Specific examples of how to access and use the data are available in the demos directory.

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

#### User Info (snowpit.coreInfo.user)
- `operationID` - ID of the operation
- `operationName` - Name of the operation
- `professional` - Boolean indicating if user is professional
- `userID` - User identifier
- `username` - SnowPilot username of the user

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

#### Weather Conditions (snowpit.coreInfo.weatherConditions)
- `skyCond` - Sky conditions code
- `skyCond_Desc` - Sky conditions description
- `precipTI` - Precipitation type and intensity code
- `precipTI_Desc` - Precipitation description
- `airTempPres` - [temperature, units]
- `windSpeed` - Wind speed code
- `windSpeed_Desc` - Wind speed description
- `windDir` - Wind direction

### 2. Snow Profile (snowpit.snowProfile)
Contains layer data and measurements:

#### Profile Info
- `measurementDirection` - Direction of measurements
- `profileDepth` - [depth, units]
- `hS` - Total snow height [value, units]

#### Layers (snowpit.snowProfile.layers)
List of Layer objects, each containing:
- `depthTop` - [depth, units]
- `thickness` - [thickness, units]
- `hardness` - Hand hardness code
- `hardnessTop` - Top of layer hardness
- `hardnessBottom` - Bottom of layer hardness
- `wetness` - Wetness code
- `wetness_Desc` - Wetness description
- `layerOfConcern` - Boolean

##### Grain Info (layer.grainFormPrimary or layer.grainFormSecondary)
- `grainForm` - Grain form code
- `grainSizeAvg` - [size, units]
- `grainSizeMax` - [size, units]
- `basicGrainClass_code` - Basic grain type code
- `basicGrainClass_name` - Basic grain type name
- `subGrainClass_code` - Detailed grain type code
- `subGrainClass_name` - Detailed grain type name

#### Temperature Profile (snowpit.snowProfile.tempProfile)
List of temperature observations, each containing:
- `depth` - [depth, units]
- `snowTemp` - [temperature, units]

#### Density Profile (snowpit.snowProfile.densityProfile)
List of density observation, each containing:
- `depthTop` - [depth, units]
- `thickness` - [thickness, units]
- `density` - [density, units]

### 3. Stability Tests (snowpit.stabilityTests)
Contains lists of different stability test results:
- `ECT` - Extended Column Test
- `CT` - Compression Test
- `RBlock` - Rutschblock Test
- `PST` - Propagation Saw Test

#### Extended Column Test (snowpit.stabilityTests.ECT) is a list of ExtColumnTest objects, each containing:
- `depthTop` - [depth, units]
- `testScore` - Test result code
- `propogation` - Boolean
- `numTaps` - Number of taps
- `comment` - Test comments

#### Compression Test (snowpit.stabilityTests.CT) is a list of ComprTest objects, each containing:
- `depthTop` - [depth, units]
- `fractureCharacter` - Fracture character code
- `testScore` - Test result code
- `comment` - Test comments

#### Rutschblock Test (snowpit.stabilityTests.RBlock) is a list of RBlockTest objects, each containing:
- `depthTop` - [depth, units]
- `fractureCharacter` - Fracture character code
- `releaseType` - Release type code
- `testScore` - Test result code
- `comment` - Test comments

#### Propagation Saw Test (snowpit.stabilityTests.PST) is a list of PropSawTest objects, each containing:
- `depthTop` - [depth, units]
- `fractureProp` - Propagation result
- `cutLength` - [length, units]
- `columnLength` - [length, units]
- `comment` - Test comments

### 4. Whumpf Data (snowpit.whumpfData)
Custom SnowPilot data about collapsing weak layers:
- `whumpfCracking` - Presence of whumpf with cracking
- `whumpfNoCracking` - Presence of whumpf without cracking
- `crackingNoWhumpf` - Presence of cracking without whumpf
- `whumpfNearPit` - Whumpf location relative to pit
- `whumpfDepthWeakLayer` - Depth of weak layer
- `whumpfTriggeredRemoteAva` - If whumpf triggered remote avalanche
- `whumpfSize` - Size of the whumpf



Resources:

https://snowpilot.org/

https://github.com/SnowpitData/AvscienceServer

http://caaml.org/Schemas/V4.2/Doc/#complexType_RescuedByBaseType_Link0BC1FC30

https://github.com/ronimos/snowpack/tree/main
