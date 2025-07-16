# SnowPylot Query Engine - Preview and Approval Feature Implementation

## Overview

I've successfully added a preview and approval system to the SnowPylot Query Engine that allows users to see how many pits will be downloaded based on their filter parameters and requests approval before proceeding with large downloads.

## New Features Added

### 1. **QueryPreview Class**
- **Location**: `src/snowpylot/query_engine.py` (lines 54-72)
- **Purpose**: Data class that holds preview information about a query
- **Fields**:
  - `estimated_count`: Number of pits that would be downloaded
  - `query_filter`: The filter parameters used
  - `preview_info`: Additional metadata about the query
- **Features**: 
  - Custom `__str__` method for formatted output
  - Shows estimated count, date range, state, organization, elevation, and format

### 2. **QueryPreview Method in QueryEngine**
- **Location**: `src/snowpylot/query_engine.py` (lines 328-365)
- **Purpose**: Preview a query without downloading all data
- **How it works**:
  - Makes a lightweight request to the snowpilot.org API
  - Uses XML endpoint with limited results to estimate total count
  - Returns a QueryPreview object with estimated pit count

### 3. **Preview Support in SnowPilotSession**
- **Location**: `src/snowpylot/query_engine.py` (lines 239-318)
- **Purpose**: Handles the actual API request for preview
- **Method**: `preview_query()`
- **How it works**:
  - Makes a request with `per_page=1` to get a sample
  - Then makes a request with `per_page=50` to get a better estimate
  - Parses XML response to count pit entries
  - Returns estimated count

### 4. **Approval System in query_pits Method**
- **Location**: `src/snowpylot/query_engine.py` (lines 366-437)
- **Purpose**: Requests user approval for large downloads
- **Parameters**:
  - `auto_approve`: If True, skip approval prompt
  - `approval_threshold`: Number of pits above which approval is required (default: 100)
- **Features**:
  - Automatically previews query before download
  - Shows warning for downloads > 1000 pits
  - Allows user to cancel download
  - Returns cancelled status in download_info if user cancels

### 5. **Updated QueryResult Class**
- **Location**: `src/snowpylot/query_engine.py` (lines 75-83)
- **New Field**: `preview: Optional[QueryPreview] = None`
- **Purpose**: Stores the preview information alongside the actual results

### 6. **New Convenience Functions**
- **Location**: `src/snowpylot/query_engine.py` (lines 645-655)
- **Function**: `preview_by_date_range()`
- **Purpose**: Convenience function to preview date range queries
- **Updated Functions**: All existing convenience functions now support `auto_approve` parameter

## Example Usage

### Basic Preview
```python
from snowpylot.query_engine import QueryEngine, QueryFilter

engine = QueryEngine()
query_filter = QueryFilter(
    date_start="2024-01-01",
    date_end="2024-01-31",
    state="MT"
)

# Preview first
preview = engine.preview_query(query_filter)
print(f"Would download {preview.estimated_count} pits")

# Then download with approval
result = engine.query_pits(query_filter, auto_approve=False, approval_threshold=100)
```

### Approval Flow
When a query exceeds the threshold, users see:
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

### Convenience Functions
```python
from snowpylot.query_engine import preview_by_date_range

# Preview using convenience function
preview = preview_by_date_range("2024-01-01", "2024-01-31", state="MT")
print(f"Preview shows {preview.estimated_count} pits available")
```

## Files Modified

1. **`src/snowpylot/query_engine.py`** - Main implementation
2. **`examples/query_engine_usage.py`** - Updated examples
3. **`examples/preview_demo.py`** - New demo script
4. **`docs/query_engine_usage.md`** - Updated documentation

## Benefits

1. **Prevents Accidental Large Downloads**: Users can see how many pits will be downloaded before proceeding
2. **Bandwidth Protection**: Automatic approval prompts for large downloads
3. **User Control**: Configurable approval thresholds
4. **Better User Experience**: Clear preview information before download
5. **Backwards Compatibility**: All existing functionality continues to work

## Technical Implementation Details

- **Preview Method**: Uses lightweight XML requests to estimate pit count
- **Approval System**: Uses Python's `input()` function for user interaction
- **Error Handling**: Graceful handling of API failures and cancellations
- **Integration**: Seamlessly integrates with existing CAAML parser and snow pit classes

The implementation is complete and ready for use! 