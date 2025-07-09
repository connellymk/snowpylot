# SnowPylot Query Engine Documentation

The SnowPylot Query Engine provides a powerful and flexible interface for downloading and querying snow pit data from snowpilot.org. It allows users to filter data based on multiple parameters and integrates seamlessly with the existing CAAML parser.

## Features

- **Flexible Filtering**: Filter by pit ID, name, date range, location, user, organization, and more
- **Multiple Data Formats**: Support for both XML and CAAML formats
- **Local Search**: Search through locally saved pit files
- **Automatic Parsing**: Automatically parses downloaded data using the existing CAAML parser
- **Session Management**: Handles authentication and session management with snowpilot.org
- **Batch Processing**: Download and process multiple pits in a single query
- **Preview Functionality**: Preview queries to see how many pits will be downloaded before proceeding
- **User Approval**: Automatic approval prompts for large downloads to prevent accidental bandwidth usage

## Installation

Ensure you have the required dependencies:

```bash
pip install requests pandas
```

## Authentication

Set your snowpilot.org credentials as environment variables:

```bash
export SNOWPILOT_USER="your_username"
export SNOWPILOT_PASSWORD="your_password"
```

## Quick Start

```python
from snowpylot.query_engine import QueryEngine, QueryFilter

# Initialize the query engine
engine = QueryEngine(pits_path="data/snowpits")

# Create a query filter
query_filter = QueryFilter(
    date_start="2024-01-01",
    date_end="2024-01-31",
    state="MT"
)

# Execute the query
result = engine.query_pits(query_filter)

# Access the results
print(f"Found {result.total_count} pits")
for pit in result.snow_pits:
    print(f"Pit: {pit.core_info.pit_name}, Date: {pit.core_info.date}")
```

## Preview Functionality

**NEW FEATURE**: Preview queries to see how many pits will be downloaded before proceeding.

### Preview a Query

```python
from snowpylot.query_engine import QueryEngine, QueryFilter

# Initialize the query engine
engine = QueryEngine()

# Create a query filter
query_filter = QueryFilter(
    date_start="2024-01-01",
    date_end="2024-01-31",
    state="MT"
)

# Preview the query first
preview = engine.preview_query(query_filter)
print(f"Preview: {preview.estimated_count} pits would be downloaded")
print(f"Date range: {preview.query_filter.date_start} to {preview.query_filter.date_end}")
print(f"State: {preview.query_filter.state}")
```

### Approval System

The query engine includes an approval system that prevents accidental large downloads:

```python
# Download with approval (will prompt if > 100 pits)
result = engine.query_pits(query_filter, auto_approve=False, approval_threshold=100)

# Auto-approve small downloads
result = engine.query_pits(query_filter, auto_approve=True)

# Custom approval threshold
result = engine.query_pits(query_filter, auto_approve=False, approval_threshold=50)
```

When the estimated pit count exceeds the threshold, users will see:
```
Query Preview:
  Estimated pits: 250
  Date range: 2024-01-01 to 2024-01-31
  State: MT
  Organization: Any
  Elevation: Any - Anym
  Format: CAAML

This query will download approximately 250 pits.
⚠️  WARNING: This is a large download that may take significant time and bandwidth.

Do you want to proceed with the download? (y/N):
```

### Preview Convenience Functions

```python
from snowpylot.query_engine import preview_by_date_range

# Preview a date range query
preview = preview_by_date_range("2024-01-01", "2024-01-31", state="MT")
print(f"Preview shows {preview.estimated_count} pits available")
```

## QueryFilter Parameters

| Parameter | Type | Description | Example |
|-----------|------|-------------|---------|
| `pit_id` | str | Specific pit ID | `"13720"` |
| `pit_name` | str | Pit name (partial match) | `"Bridger Ridge"` |
| `date_start` | str | Start date (YYYY-MM-DD) | `"2024-01-01"` |
| `date_end` | str | End date (YYYY-MM-DD) | `"2024-01-31"` |
| `country` | str | Country code | `"US"` |
| `state` | str | State/region code | `"MT"` |
| `user_id` | str | User ID | `"6739"` |
| `username` | str | Username (partial match) | `"benschmidt5"` |
| `organization_id` | str | Organization ID | `"316"` |
| `organization_name` | str | Organization name (partial match) | `"Montana Avalanche Center"` |
| `elevation_min` | float | Minimum elevation (meters) | `2000.0` |
| `elevation_max` | float | Maximum elevation (meters) | `3000.0` |
| `aspect` | str | Slope aspect | `"N"`, `"NE"`, `"E"`, etc. |
| `per_page` | int | Results per page | `1000` |

## Usage Examples

### 1. Query by Date Range and State

```python
from snowpylot.query_engine import QueryEngine, QueryFilter

query_filter = QueryFilter(
    date_start="2024-01-01",
    date_end="2024-01-31",
    state="MT"
)

engine = QueryEngine()
result = engine.query_pits(query_filter)
print(f"Found {result.total_count} pits from Montana in January 2024")
```

### 2. Query by Organization

```python
query_filter = QueryFilter(
    organization_name="Montana Avalanche Center",
    date_start="2024-01-01",
    date_end="2024-12-31"
)

result = engine.query_pits(query_filter)
print(f"Found {result.total_count} pits from Montana Avalanche Center")
```

### 3. Query by Elevation Range

```python
query_filter = QueryFilter(
    elevation_min=2500,
    elevation_max=3500,
    state="CO"
)

result = engine.query_pits(query_filter)
print(f"Found {result.total_count} pits between 2500m and 3500m in Colorado")
```

### 4. Query by Specific Pit ID

```python
query_filter = QueryFilter(pit_id="13720")
result = engine.query_pits(query_filter)

if result.total_count > 0:
    pit = result.snow_pits[0]
    print(f"Found pit: {pit.core_info.pit_name}")
    print(f"Date: {pit.core_info.date}")
    print(f"User: {pit.core_info.user.username}")
```

### 5. Complex Multi-Parameter Query

```python
query_filter = QueryFilter(
    date_start="2024-01-01",
    date_end="2024-03-31",
    state="MT",
    elevation_min=2000,
    aspect="N",
    organization_name="Avalanche Center"
)

result = engine.query_pits(query_filter)
print(f"Found {result.total_count} north-facing pits above 2000m")
```

### 6. Search Local Files

```python
# Search through locally saved pit files
query_filter = QueryFilter(
    state="MT",
    elevation_min=2000
)

result = engine.search_local_pits(query_filter)
print(f"Found {result.total_count} local pits")
print(f"Searched {result.download_info['files_searched']} files")
```

## Convenience Functions

The query engine provides several convenience functions for common use cases:

### Query by Date Range
```python
from snowpylot.query_engine import query_by_date_range

result = query_by_date_range("2024-01-01", "2024-01-31", state="MT")
```

### Query by Pit ID
```python
from snowpylot.query_engine import query_by_pit_id

result = query_by_pit_id("13720")
```

### Query by Organization
```python
from snowpylot.query_engine import query_by_organization

result = query_by_organization("Montana Avalanche Center", 
                              date_start="2024-01-01", 
                              date_end="2024-12-31")
```

### Query by Location
```python
from snowpylot.query_engine import query_by_location

result = query_by_location(country="US", state="MT", 
                          elevation_min=2000, elevation_max=3000)
```

## Data Formats

The query engine supports two data formats:

### CAAML Format (Recommended)
```python
result = engine.query_pits(query_filter, data_format="caaml")
```
- Downloads individual CAAML XML files for each pit
- Fully compatible with the existing CAAML parser
- Includes all pit data and metadata

### XML Format
```python
result = engine.query_pits(query_filter, data_format="xml")
```
- Downloads bulk XML data
- Faster for large queries
- May require additional processing

## Working with Results

The `QueryResult` object contains:

```python
class QueryResult:
    snow_pits: List[SnowPit]        # List of parsed SnowPit objects
    total_count: int                 # Total number of pits found
    query_filter: QueryFilter        # Original query filter
    download_info: Dict[str, Any]    # Information about the download
```

### Accessing Pit Data

```python
result = engine.query_pits(query_filter)

for pit in result.snow_pits:
    # Core information
    print(f"Pit ID: {pit.core_info.pit_id}")
    print(f"Name: {pit.core_info.pit_name}")
    print(f"Date: {pit.core_info.date}")
    
    # User information
    print(f"User: {pit.core_info.user.username}")
    print(f"Organization: {pit.core_info.user.operation_name}")
    
    # Location information
    print(f"Country: {pit.core_info.location.country}")
    print(f"State: {pit.core_info.location.region}")
    print(f"Elevation: {pit.core_info.location.elevation}")
    print(f"Aspect: {pit.core_info.location.aspect}")
    
    # Snow profile data
    print(f"Profile depth: {pit.snow_profile.profile_depth}")
    print(f"Number of layers: {len(pit.snow_profile.layers)}")
    
    # Stability tests
    print(f"Compression tests: {len(pit.stability_tests.compression_tests)}")
    print(f"Extended column tests: {len(pit.stability_tests.extended_column_tests)}")
```

## Supported States

The query engine supports the following US states:

| State | Code | ID |
|-------|------|-----|
| Montana | MT | 27 |
| Colorado | CO | 8 |
| Wyoming | WY | 51 |
| Utah | UT | 45 |
| Idaho | ID | 16 |
| Washington | WA | 48 |
| Oregon | OR | 41 |
| California | CA | 6 |
| Alaska | AK | 2 |
| New Hampshire | NH | 33 |
| Vermont | VT | 46 |
| Maine | ME | 23 |
| New York | NY | 36 |

## Error Handling

The query engine includes comprehensive error handling:

```python
try:
    result = engine.query_pits(query_filter)
    if result.total_count == 0:
        print("No pits found matching the criteria")
    else:
        print(f"Successfully found {result.total_count} pits")
except Exception as e:
    print(f"Query failed: {e}")
```

## Performance Tips

1. **Use date ranges**: Always specify date ranges to limit the scope of queries
2. **Use state filters**: Filtering by state significantly reduces query time
3. **CAAML format**: Use CAAML format for better integration with existing parsers
4. **Batch processing**: Process multiple pits in a single query rather than individual requests
5. **Local search**: Use `search_local_pits()` to query previously downloaded data

## Advanced Usage

### Custom Pit Storage Path

```python
engine = QueryEngine(pits_path="/custom/path/to/pits")
```

### Processing Large Datasets

```python
# Query in chunks for large date ranges
from datetime import datetime, timedelta

start_date = datetime(2024, 1, 1)
end_date = datetime(2024, 12, 31)
chunk_size = timedelta(days=30)

all_pits = []
current_date = start_date

while current_date < end_date:
    chunk_end = min(current_date + chunk_size, end_date)
    
    query_filter = QueryFilter(
        date_start=current_date.strftime("%Y-%m-%d"),
        date_end=chunk_end.strftime("%Y-%m-%d"),
        state="MT"
    )
    
    result = engine.query_pits(query_filter)
    all_pits.extend(result.snow_pits)
    
    current_date = chunk_end

print(f"Total pits processed: {len(all_pits)}")
```

## Integration with Existing Code

The query engine is designed to work seamlessly with the existing SnowPylot codebase:

```python
from snowpylot.query_engine import QueryEngine, QueryFilter
from snowpylot.caaml_parser import caaml_parser

# Query and download pits
engine = QueryEngine()
query_filter = QueryFilter(state="MT", date_start="2024-01-01", date_end="2024-01-31")
result = engine.query_pits(query_filter)

# The returned SnowPit objects are fully compatible with existing code
for pit in result.snow_pits:
    # Use existing SnowPit methods
    print(pit.core_info)
    print(pit.snow_profile)
    print(pit.stability_tests)
```

## Troubleshooting

### Authentication Issues
- Ensure `SNOWPILOT_USER` and `SNOWPILOT_PASSWORD` are set correctly
- Check that your snowpilot.org account has API access
- Verify your credentials by logging in to snowpilot.org manually

### No Data Returned
- Check if the date range contains any pits
- Verify that the state code is correct
- Try a broader query first, then narrow down with filters

### Performance Issues
- Use smaller date ranges
- Add state filters to reduce query scope
- Consider using local search for repeated queries

### File Permission Errors
- Ensure the pit storage directory is writable
- Check available disk space
- Verify file path permissions

## Examples

See `examples/query_engine_usage.py` for comprehensive usage examples demonstrating all features of the query engine.

## API Reference

For detailed API documentation, see the docstrings in the `query_engine.py` module. 