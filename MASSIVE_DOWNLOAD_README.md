# Massive Snowpit Download Guide

This guide explains how to download all snowpits from October 1, 2002 to July 31, 2024 using the adaptive chunking system.

## Overview

The massive download script (`massive_snowpit_download.py`) uses an intelligent chunking strategy that adapts to seasonal patterns in snowpit frequency:

- **Winter Peak (Dec-Feb)**: 7-day chunks (high snowpit density)
- **Winter (Nov, Mar-Apr)**: 14-day chunks (moderate snowpit density) 
- **Shoulder Seasons (May, Oct)**: 30-day chunks (lower snowpit density)
- **Summer (Jun-Sep)**: 60-day chunks (lowest snowpit density)

## Prerequisites

1. **Authentication**: Ensure your SnowPilot credentials are set:
   - Username: `katisthebatis`
   - Password: `mkconn123`

2. **Dependencies**: All required packages should be installed via the project's requirements

3. **Storage**: Ensure you have sufficient disk space. Expect 10-50 GB for the complete dataset.

## Usage

### Step 1: Prepare the Environment

```bash
# Navigate to the project directory
cd /path/to/snowpylot

# Apply critical fixes to the query engine (recommended)
python query_engine_fixes.py
```

### Step 2: Run the Massive Download

```bash
python massive_snowpit_download.py
```

The script will:
1. Test authentication
2. Generate adaptive chunks based on seasonal patterns
3. Check for any previously completed chunks (resume capability)
4. Show estimated download time
5. Ask for confirmation before starting
6. Begin the download with progress tracking

### Step 3: Monitor Progress

The script provides several ways to monitor progress:

1. **Console Output**: Real-time progress with chunk-by-chunk updates
2. **Log File**: Detailed logging in `massive_download.log`
3. **Progress File**: JSON tracking in `download_progress.json`

## Key Features

### 🧠 Adaptive Chunking
- Automatically adjusts chunk size based on season
- Reduces API calls while staying under the 100-pit limit
- Optimized for snowpit frequency patterns

### 📊 Progress Tracking
- Saves progress to `download_progress.json`
- Resume capability if download is interrupted
- Detailed statistics and error tracking

### ⏱️ Rate Limiting
- 60-second delays between chunks to avoid API caching issues
- Configurable delay timing
- Respects SnowPilot.org rate limits

### 🔄 Robust Error Handling
- Automatic retries for failed chunks
- Comprehensive error logging
- Graceful handling of network issues

## Expected Timeline

For the complete dataset (Oct 2002 - Jul 2024):

- **Estimated Chunks**: ~400-500 chunks
- **Estimated Time**: 8-12 hours (with 60s delays)
- **Peak Hours**: Avoid running during SnowPilot.org peak usage

## File Structure

After completion, your data will be organized as:

```
data/massive_snowpit_download/
├── 2002-10-01_2002-10-31_20240803_123456_pits/
├── 2002-11-01_2002-11-07_20240803_123458_pits/
├── ... (hundreds of chunk directories)
└── download_progress.json
```

Each chunk directory contains:
- Extracted CAAML XML files
- Organized by date range

## Troubleshooting

### Common Issues

1. **Authentication Failed**
   - Verify credentials are correct
   - Check if account is active on SnowPilot.org

2. **Download Interrupted**
   - Simply re-run the script - it will resume from where it left off
   - Check `download_progress.json` for current status

3. **Some Chunks Failed**
   - Review `massive_download.log` for error details
   - Failed chunks will be retried on next run
   - Consider increasing delay for problematic time periods

4. **Disk Space Issues**
   - Monitor available disk space during download
   - Consider downloading in smaller date ranges if needed

### Advanced Configuration

You can modify the script to adjust:

- `DELAY_BETWEEN_CHUNKS`: Increase if hitting rate limits
- Seasonal chunk sizes in `AdaptiveChunkStrategy`
- Download path in `DOWNLOAD_PATH`
- Date range by modifying `START_DATE` and `END_DATE`

## Data Quality Notes

### Expected Patterns

- **Early years (2002-2005)**: Fewer snowpits as the platform was new
- **Growth period (2006-2015)**: Steady increase in adoption
- **Modern era (2016-2024)**: High density, especially in winter months

### Data Gaps

Some periods may have no data due to:
- Platform downtime or maintenance
- Regional variations in usage
- Seasonal patterns (summer months naturally have fewer snowpits)

## Performance Tips

1. **Run during off-peak hours**: Avoid 9 AM - 5 PM MST when SnowPilot.org usage is highest
2. **Stable internet**: Ensure reliable connection for 8-12 hour download
3. **Monitor system resources**: Watch disk space and memory usage
4. **Consider region-specific downloads**: For faster regional analysis

## Support

If you encounter issues:

1. Check the log file: `massive_download.log`
2. Review progress file: `download_progress.json`
3. Try increasing the delay between chunks
4. Consider downloading smaller date ranges for testing

The script is designed to be robust and resumable, so most issues can be resolved by simply re-running the script.