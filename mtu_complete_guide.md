# MTU (Marketing Touch Users) Complete Guide

## Current Status: SEGMENT COUNTS LIMITATION

**CRITICAL FINDING**: MoEngage APIs do not provide programmatic access to segment user counts. After extensive research of MoEngage's API documentation, the following APIs are available:

✅ **Available APIs:**
- Create Custom Segments API
- List Custom Segments API  
- Get Segment by ID API
- Update/Archive Segments API

❌ **Missing Functionality:**
- **No API returns segment user counts**
- **No Analytics/Reporting API for segment sizes**
- **No programmatic way to get segment counts**

## Solution: Semi-Automated Workflow

Since MoEngage doesn't provide segment counts via API, we've implemented a **semi-automated solution**:

1. **Automated**: Create all required segments via API
2. **Manual**: Fetch segment counts from MoEngage dashboard  
3. **Automated**: Calculate MTU percentages and update Google Sheets

## Complete Workflow

### Step 1: Create MTU Segments (Automated)

```bash
python mtu_segment_creator.py
```

**What it does:**
- Creates 12 segments total (6 for UK, 6 for UAE)
- Each country gets:
  - All Users segment
  - Active Users (60 days) segment  
  - Push Received segment
  - Push Received (Active) segment
  - Email Received segment
  - Email Received (Active) segment

**Input required:**
- End date for the calculation period (YYYY-MM-DD format)

**Output:**
- 12 segments created in MoEngage
- Segment IDs and names printed for reference

### Step 2: Fetch Segment Counts (Manual)

1. Go to MoEngage Dashboard → Segments
2. Find each segment created in Step 1 (they have MTU_ prefix)
3. Note down the user count for each segment
4. Keep these numbers ready for Step 3

**Segments to find:**
- `MTU_UK_AllUsers_[timestamp]`
- `MTU_UK_Active60d_[timestamp]`  
- `MTU_UK_PushReceived_[timestamp]`
- `MTU_UK_PushActive60d_[timestamp]`
- `MTU_UK_EmailReceived_[timestamp]`
- `MTU_UK_EmailActive60d_[timestamp]`
- `MTU_AE_AllUsers_[timestamp]`
- `MTU_AE_Active60d_[timestamp]`
- `MTU_AE_PushReceived_[timestamp]`
- `MTU_AE_PushActive60d_[timestamp]`
- `MTU_AE_EmailReceived_[timestamp]`
- `MTU_AE_EmailActive60d_[timestamp]`

### Step 3: Calculate MTU and Update Sheets (Automated)

```bash
python mtu_calculator.py
```

**What it does:**
- Prompts you to enter the segment counts from Step 2
- Calculates MTU percentages using the formula:
  - **MTU = (Active users who received comms / Active users) × 100**
- Updates Google Sheets with results in vertical format
- Saves results to JSON file for record keeping

**Calculations performed:**
- Active user percentage per country
- MTU percentage for Push (per country)
- MTU percentage for Email (per country)  
- Reach percentage for each channel
- All formatted and organized in Google Sheets

## MTU Calculation Formula

Based on the MTU method PDF requirements:

```
MTU (Marketing Touch Users) = (Active users who received communications / Total active users) × 100

Where:
- Active users = Users who made a transaction in last 60 days
- Communications = Push notifications or Email campaigns sent in the period
- Period = Month start to selected end date
```

## Files Created

### Core Scripts
- `mtu_segment_creator.py` - Creates all required segments in MoEngage
- `mtu_calculator.py` - Calculates MTU from manual counts and updates Google Sheets
- `test_segment_api.py` - Tests segment APIs (confirms no count data available)

### Configuration
- `google_credentials.json` - Google Sheets API credentials
- `mtu_results_[timestamp].json` - Saved calculation results

### Documentation  
- `mtu_setup_guide.md` - Original setup documentation
- `mtu_complete_guide.md` - This comprehensive guide

## Google Sheets Integration

**Sheet ID**: `1A30FfO319eiKW0c6zHj2lwr04WLE0fL6eLteZf4CvHM`
**Worksheet**: "MTU Metrics" (created automatically)

**Data Format** (Vertical Layout):
```
MTU Metrics Report
Generated: 2026-02-02 15:30:00
Period: January 2026

Metric              UK        UAE
All Users           50,000    30,000
Active Users (60d)  15,000    9,000
Active %            30%       30%

Push Received       8,000     5,000
Push Received (Active) 4,000  2,500
Push MTU %          26.7%     27.8%
Push Reach %        16%       16.7%

Email Received      12,000    7,000
Email Received (Active) 6,000 3,500
Email MTU %         40%       38.9%
Email Reach %       24%       23.3%
```

## API Credentials Used

**MoEngage DATA API:**
- Workspace ID: `95PNUHBSYSLLJZ22PEOFMKF2`
- DATA API Key: `Mj5JSGKcwYum9NKAGmGHJG_E`
- Data Center: `01`

**Google Sheets API:**
- Service Account credentials in `google_credentials.json`
- Scopes: Google Sheets and Google Drive

## Troubleshooting

### Common Issues

1. **"Segment not found in dashboard"**
   - Check the segment name includes timestamp
   - Look for MTU_ prefix
   - Segments may take a few minutes to appear

2. **"Google Sheets permission denied"**
   - Ensure service account has edit access to the sheet
   - Check credentials file is valid

3. **"API authentication failed"**
   - Verify MoEngage credentials are correct
   - Check data center number (01)

### Alternative Approaches Considered

1. **Web Scraping MoEngage Dashboard**
   - Technically possible but fragile
   - Would break with UI changes
   - Against terms of service

2. **MoEngage Data Export API**
   - Designed for user-level data export
   - Not suitable for segment counts
   - Would require processing millions of records

3. **Campaign API Stats**
   - Only provides campaign performance data
   - No segment size information

## Future Improvements

If MoEngage adds segment count APIs in the future:

1. **Fully Automated Workflow**
   - Create segments → Get counts → Calculate MTU → Update sheets
   - Could run on schedule (daily/weekly)

2. **Historical Tracking**
   - Store MTU trends over time
   - Automated alerts for significant changes

3. **Advanced Analytics**
   - Segment overlap analysis
   - Channel effectiveness comparison
   - Predictive MTU modeling

## Conclusion

While MoEngage's API limitations prevent fully automated segment count retrieval, this semi-automated solution provides:

✅ **Automated segment creation** (saves manual work)
✅ **Automated MTU calculations** (eliminates formula errors)  
✅ **Automated Google Sheets updates** (consistent formatting)
✅ **Data persistence** (JSON backups)
✅ **Scalable approach** (easy to modify for new requirements)

The manual step of fetching segment counts from the dashboard is unavoidable with current MoEngage API capabilities, but the workflow minimizes manual work and ensures accurate, consistent results.