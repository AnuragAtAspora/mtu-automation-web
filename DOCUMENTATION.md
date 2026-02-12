# MoEngage Metrics Automation - Complete Documentation

## 📋 Table of Contents
1. [Project Overview](#project-overview)
2. [Architecture & Components](#architecture--components)
3. [API Integration](#api-integration)
4. [Application Flow](#application-flow)
5. [Metrics Calculation Logic](#metrics-calculation-logic)
6. [Segments Structure](#segments-structure)
7. [Limitations & Constraints](#limitations--constraints)
8. [Deployment](#deployment)
9. [Troubleshooting](#troubleshooting)

---

## 📊 Project Overview

### Purpose
Automated calculation of communication metrics for MoEngage campaigns across UK and UAE markets, tracking both promotional (one-time) and transactional (event-triggered) campaigns.

### Key Features
- Automated segment creation in MoEngage
- Campaign data fetching and aggregation
- Metrics calculation for 6 key performance indicators
- CSV export for detailed campaign analysis
- Support for both Push Notifications and Email channels

### Technology Stack
- **Backend**: Python 3.9, Flask
- **Deployment**: Railway (PaaS)
- **APIs**: MoEngage Segmentation API, Campaign Meta API, Stats API
- **Storage**: File-based caching, JSON configuration files

---

## 🏗️ Architecture & Components

### Project Structure
```
├── app.py                          # Main Flask application
├── config.py                       # Configuration settings
├── modules/
│   ├── __init__.py
│   ├── segment_creator.py          # Segment creation logic
│   ├── campaign_fetcher.py         # Campaign data fetching
│   └── metrics_calculator.py       # Metrics calculation
├── templates/
│   ├── base.html                   # Base template
│   ├── index.html                  # Date selection page
│   ├── segments_created.html       # Segment count input page
│   ├── results.html                # Metrics display page
│   └── settings.html               # Transactional campaign config
├── transactional_campaigns.json    # Transactional campaign IDs
├── Procfile                        # Railway deployment config
├── requirements.txt                # Python dependencies
└── runtime.txt                     # Python version

```

### Core Modules

#### 1. **app.py** - Main Application
- Flask routes and request handling
- Session management (2-hour permanent sessions)
- File-based caching for large datasets
- CSV generation and download

#### 2. **segment_creator.py** - Segment Management
- Creates 18 segments in MoEngage
- Handles segment reuse (409 conflicts)
- Rate limiting (1 second between API calls)
- Supports both UK and UAE markets

#### 3. **campaign_fetcher.py** - Campaign Data
- Fetches promotional campaigns via Campaign Meta API
- Fetches transactional campaigns via Stats API
- Parallel API calls (10 workers) for performance
- Handles pagination and rate limiting

#### 4. **metrics_calculator.py** - Metrics Engine
- Calculates 6 key metrics per country
- Aggregates campaign data by category
- Handles division by zero gracefully

---

## 🔌 API Integration

### MoEngage APIs Used

#### 1. **Segmentation API** (Data API)
**Endpoint**: `https://api-01.moengage.com/v3/custom-segments/`

**Authentication**: Basic Auth (Workspace ID + Data API Key)

**Purpose**: Create user segments for counting

**Rate Limit**: 1 request/second (implemented in code)

**Payload Example**:
```json
{
  "name": "UK_All_Users_20260209_143025",
  "description": "All UK users",
  "included_filters": {
    "filter_operator": "and",
    "filters": [
      {
        "filter_type": "user_attributes",
        "name": "country",
        "data_type": "string",
        "operator": "in",
        "value": ["GB"],
        "negate": false,
        "case_sensitive": false
      }
    ]
  }
}
```

#### 2. **Campaign Meta API** (Campaign API)
**Endpoint**: `https://api-01.moengage.com/core-services/v1/campaigns/meta`

**Authentication**: Basic Auth (Workspace ID + Campaign API Key)

**Purpose**: 
- Fetch promotional campaigns by creation date
- Get campaign metadata (name, channel, delivery type)
- Validate transactional campaign IDs

**Pagination**: Max 15 campaigns per page

**Date Format**: YYYY-MM-DD (ISO format)

**Payload Example**:
```json
{
  "request_id": "meta_date_1707500000",
  "page": 1,
  "limit": 15,
  "campaign_fields": {
    "created_date": {
      "from_date": "2026-02-01",
      "to_date": "2026-02-08"
    }
  }
}
```

#### 3. **Stats API** (Campaign API)
**Endpoint**: `https://api-01.moengage.com/core-services/v1/campaign-stats`

**Authentication**: Basic Auth (Workspace ID + Campaign API Key)

**Purpose**: Fetch campaign performance metrics

**Batch Size**: Max 10 campaign IDs per request

**Date Format**: YYYY-MM-DD (ISO format)

**Payload Example**:
```json
{
  "request_id": "stats_batch_1707500000",
  "campaign_ids": ["campaign_id_1", "campaign_id_2"],
  "start_date": "2026-02-01",
  "end_date": "2026-02-08",
  "attribution_type": "VIEW_THROUGH",
  "metric_type": "TOTAL"
}
```

**Response Structure**:
```json
{
  "data": {
    "campaign_id_1": [
      {
        "platforms": {
          "ALL_PLATFORMS": {
            "locales": {
              "all_locale": {
                "variations": {
                  "all_variations": {
                    "performance_stats": {
                      "sent": 1000,
                      "delivered": 950,
                      "open": 200,
                      "click": 50,
                      "unsubscribe": 5,
                      "bounced": 30,
                      "failed": 20
                    }
                  }
                }
              }
            }
          }
        }
      }
    ]
  }
}
```

**Important Notes**:
- `open` field = Unique Opens (not total)
- `click` field = Unique Clicks (not total)
- Use `ALL_PLATFORMS` to avoid double counting
- Field is `'open'` not `'opened'`
- Field is `'bounced'` not `'bounce'`

---

## 🔄 Application Flow

### Step 1: Date Selection
**Route**: `/` (GET)

**User Action**: Select start and end dates

**Output**: Redirects to segment creation

---

### Step 2: Segment Creation
**Route**: `/create-segments` (POST)

**Process**:
1. Receives date range from form
2. Creates 18 segments in MoEngage:
   - 9 UK segments
   - 9 UAE segments
3. Each segment gets a unique timestamp-based name
4. Handles existing segments (409 conflict → reuse)

**Segments Created**:
- Total Users
- Active Users (60 days)
- Transacted Users (selected period)
- Received Push
- Received Email
- Active + Received Push
- Active + Received Email
- Unsubscribed Push
- Unsubscribed Email

**Output**: Displays segment links and count input form

**Time**: ~18-20 seconds (18 segments × 1 second rate limit)

---

### Step 3: Manual Count Entry
**Route**: `/segments_created.html` (displayed after Step 2)

**User Action**: 
1. Open each segment link in MoEngage
2. Note the user count shown
3. Enter counts in the form (18 fields total)

**Why Manual?**: MoEngage Segmentation API doesn't return segment counts immediately; segments need time to compute.

---

### Step 4: Campaign Fetching & Metrics Calculation
**Route**: `/calculate-metrics` (POST)

**Process**:

#### 4.1 Fetch Promotional Campaigns
- Use Campaign Meta API with `created_date` filter
- Filter for `delivery_type = ONE_TIME`
- Fetch up to 100 pages (1,500 campaigns max)
- Get campaign IDs

#### 4.2 Fetch Promotional Campaign Stats
- Batch fetch stats (10 campaigns per API call)
- Use Stats API with date range
- Extract: sent, delivered, open, click, unsubscribe, bounce, failed

#### 4.3 Fetch Transactional Campaigns
- Load campaign IDs from `transactional_campaigns.json`
- Batch fetch stats (10 campaigns per API call)
- Use Stats API with date range

#### 4.4 Categorize Campaigns
Group into 8 categories:
- UK Promotional Push
- UK Promotional Email
- UK Transactional Push
- UK Transactional Email
- UAE Promotional Push
- UAE Promotional Email
- UAE Transactional Push
- UAE Transactional Email

**Categorization Logic**:
```python
# Country detection
if campaign.country == 'UK' or 'uk' in campaign_name or 'gb' in campaign_name:
    country = 'UK'
elif campaign.country == 'UAE' or 'uae' in campaign_name or 'ae' in campaign_name:
    country = 'UAE'

# Channel detection
if channel in ['push', 'android', 'ios'] or 'push' in campaign_name:
    channel_type = 'push'
elif channel == 'email' or 'email' in campaign_name:
    channel_type = 'email'

# Type detection
if delivery_type == 'ONE_TIME':
    type = 'promotional'
elif delivery_type == 'EVENT_TRIGGERED':
    type = 'transactional'
```

#### 4.5 Calculate Metrics
- Aggregate campaign data by category
- Calculate 6 metrics per country
- Store in file-based cache

**Output**: Displays metrics results page

**Time**: ~30-60 seconds (depends on campaign count)

---

### Step 5: Results & CSV Download
**Route**: `/download-csv/<category>` (GET)

**Available Downloads**: 8 CSV files (one per category)

**CSV Format**:
- **Promotional**: Campaign Name, Sent Day, Nature, Total Sent, Unique Clicks/Opens
- **Transactional**: Campaign Name, Period (date range), Nature, Total Sent, Unique Clicks/Opens

---

## 📈 Metrics Calculation Logic

### Metric 1: % Receiving Comms (Total Userbase)

**Purpose**: Percentage of total users who received communications

**Formula**:
```
PN:    (push_received / total_users) × 100
Email: (email_received / total_users) × 100
```

**Data Sources**:
- Numerator: Segment count (users who received push/email)
- Denominator: Segment count (total users)

**Example**:
- UK Total Users: 100,000
- UK Push Received: 45,000
- Result: 45.00%

---

### Metric 2: Unsubscribe Rate

**Purpose**: Percentage of total users who unsubscribed

**Formula**:
```
PN:    (push_unsubscribed / total_users) × 100
Email: (email_unsubscribed / total_users) × 100
```

**Data Sources**:
- Numerator: Segment count (users who unsubscribed)
- Denominator: Segment count (total users)

**Important**: Denominator is total users, NOT users who received comms

**Example**:
- UK Total Users: 100,000
- UK Push Unsubscribed: 500
- Result: 0.50%

---

### Metric 3: % Receiving Comms (Active Userbase)

**Purpose**: Percentage of active users who received communications

**Formula**:
```
PN:    (push_received_active / active_users) × 100
Email: (email_received_active / active_users) × 100
```

**Data Sources**:
- Numerator: Segment count (active users who received push/email)
- Denominator: Segment count (active users - transacted in last 60 days)

**Active User Definition**: Users with ORDER event (sub_event = COMPLETED or PAYMENT_COMPLETED) in last 60 days

**Example**:
- UK Active Users: 25,000
- UK Active + Push Received: 18,000
- Result: 72.00%

---

### Metric 4: No. of Comms Received per User

**Purpose**: Average number of communications sent per user

**Formula**:
```
Transactional PN:    tx_pn_sent / transacted_users
Transactional Email: tx_email_sent / transacted_users
Promotional PN:      pr_pn_sent / total_users
Promotional Email:   pr_email_sent / total_users
```

**Data Sources**:
- Numerator: Sum of campaign 'sent' values (from Stats API)
- Denominator: 
  - Transactional: Segment count (users who transacted in period)
  - Promotional: Segment count (total users)

**Important**: Different denominators for transactional vs promotional

**Example (Transactional)**:
- UK Transactional Push Sent: 50,000
- UK Transacted Users: 10,000
- Result: 5.00 comms per user

**Example (Promotional)**:
- UK Promotional Push Sent: 200,000
- UK Total Users: 100,000
- Result: 2.00 comms per user

---

### Metric 5: PN CTR (Click-Through Rate)

**Purpose**: Percentage of push notifications that were clicked

**Formula**:
```
UK:  (uk_pn_clicks / uk_pn_sent) × 100
UAE: (uae_pn_clicks / uae_pn_sent) × 100
```

**Data Sources**:
- Numerator: Sum of 'click' values for all push campaigns (promotional + transactional)
- Denominator: Sum of 'sent' values for all push campaigns (promotional + transactional)

**Important**: Uses unique clicks, not total clicks

**Example**:
- UK Total Push Sent: 250,000
- UK Total Push Clicks: 7,500
- Result: 3.00%

---

### Metric 6: Email Open Rate

**Purpose**: Percentage of emails that were opened

**Formula**:
```
UK:  (uk_email_opens / uk_email_sent) × 100
UAE: (uae_email_opens / uae_email_sent) × 100
```

**Data Sources**:
- Numerator: Sum of 'open' values for all email campaigns (promotional + transactional)
- Denominator: Sum of 'sent' values for all email campaigns (promotional + transactional)

**Important**: Uses unique opens, not total opens

**Example**:
- UK Total Email Sent: 150,000
- UK Total Email Opens: 30,000
- Result: 20.00%

---

## 🎯 Segments Structure

### Segment Naming Convention
```
{Country}_{Type}_{Timestamp}
```

Example: `UK_All_Users_20260209_143025`

### Segment Definitions

#### 1. Total Users
**Filter**: Country = GB/AE

**Purpose**: Baseline user count

---

#### 2. Active Users (60 days)
**Filter**: 
- Country = GB/AE
- ORDER event in last 60 days
- sub_event = COMPLETED OR PAYMENT_COMPLETED

**Purpose**: Users who transacted recently

---

#### 3. Transacted Users (Period)
**Filter**:
- Country = GB/AE
- ORDER event between start_date and end_date
- sub_event = COMPLETED OR PAYMENT_COMPLETED

**Purpose**: Users who transacted during analysis period

---

#### 4. Received Push
**Filter**:
- Country = GB/AE
- (NOTIFICATION_RECEIVED_MOE OR n_i_s) between start_date and end_date

**Purpose**: Users who received push notifications

**Note**: Uses OR logic to combine Android (NOTIFICATION_RECEIVED_MOE) and iOS (n_i_s) events

---

#### 5. Received Email
**Filter**:
- Country = GB/AE
- MOE_EMAIL_SENT between start_date and end_date

**Purpose**: Users who received emails

---

#### 6. Active + Received Push
**Filter**:
- Country = GB/AE
- (NOTIFICATION_RECEIVED_MOE OR n_i_s) in last 60 days
- ORDER event in last 60 days (sub_event = COMPLETED OR PAYMENT_COMPLETED)

**Purpose**: Active users who received push

---

#### 7. Active + Received Email
**Filter**:
- Country = GB/AE
- MOE_EMAIL_SENT between start_date and end_date
- ORDER event in last 60 days (sub_event = COMPLETED OR PAYMENT_COMPLETED)

**Purpose**: Active users who received email

---

#### 8. Unsubscribed Push
**Filter**:
- Country = GB/AE
- MOE_PUSH_PERMISSION_STATE_BLOCKED between start_date and end_date

**Purpose**: Users who blocked push notifications

---

#### 9. Unsubscribed Email
**Filter**:
- Country = GB/AE
- MOE_EMAIL_UNSUBSCRIBE between start_date and end_date

**Purpose**: Users who unsubscribed from emails

---

## ⚠️ Limitations & Constraints

### API Limitations

#### 1. **Campaign Meta API**
- Max 15 campaigns per page
- No direct filtering by `campaign_start_time` (when sent)
- Only filters by `created_date` (when created in dashboard)
- Requires pagination for large datasets

#### 2. **Stats API**
- Max 10 campaign IDs per request
- Requires batching for large campaign lists
- Complex nested response structure
- Field names: `'open'` not `'opened'`, `'bounced'` not `'bounce'`

#### 3. **Segmentation API**
- Rate limit: 1 request/second (enforced in code)
- Segments take time to compute (not instant)
- No API to retrieve segment counts (manual entry required)
- 409 conflict when segment name exists (handled by reusing)

### Application Limitations

#### 1. **Campaign Fetching**
- Max 100 pages from Campaign Meta API (1,500 campaigns)
- Configurable via `MAX_CAMPAIGN_PAGES` in config.py
- Timeout: 300 seconds (5 minutes) for Gunicorn workers

#### 2. **Session Management**
- 2-hour session timeout
- File-based cache for large datasets
- Cache stored in temp directory (may be cleared on restart)

#### 3. **Transactional Campaigns**
- Requires manual configuration in Settings page
- Must be added before metrics calculation
- No automatic discovery of transactional campaigns

#### 4. **Date Handling**
- Promotional campaigns: Filtered by `created_date` (proxy for sent date)
- Transactional campaigns: Stats aggregated for entire period
- Assumption: `created_date` ≈ `campaign_start_time` for promotional campaigns

### Known Issues

#### 1. **Transactional Campaign Data**
**Issue**: Stats may appear to be from a single day instead of the full period

**Possible Cause**: Stats API may interpret date ranges differently for EVENT_TRIGGERED campaigns

**Workaround**: Currently under investigation with debug logging

#### 2. **Double Counting Prevention**
**Solution**: Use `ALL_PLATFORMS` aggregate instead of summing individual platforms (IOS, ANDROID, UNKNOWN)

**Why**: Stats API returns both individual platform data AND an aggregate, which would cause 2x values if summed

#### 3. **Campaign Categorization**
**Challenge**: Inferring country from campaign name for promotional campaigns

**Logic**: 
- Check explicit `country` field (transactional only)
- Fall back to name matching: 'uk', 'gb' → UK; 'uae', 'ae' → UAE

---

## 🚀 Deployment

### Platform: Railway

**URL**: https://web-production-c1afd.up.railway.app/

### Configuration Files

#### 1. **Procfile**
```
web: gunicorn app:app --timeout 300 --workers 2
```

- Timeout: 300 seconds (5 minutes)
- Workers: 2 (for parallel request handling)

#### 2. **railway.json**
```json
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "startCommand": "gunicorn app:app --timeout 300 --workers 2",
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 10
  }
}
```

#### 3. **runtime.txt**
```
python-3.9.21
```

### Environment Variables

Set in Railway dashboard:

```
MOENGAGE_WORKSPACE_ID=95PNUHBSYSLLJZ22PEOFMKF2
MOENGAGE_DATA_API_KEY=Mj5JSGKcwYum9NKAGmGHJG_E
MOENGAGE_CAMPAIGN_API_KEY=3XMHJ83D2X4V
MOENGAGE_DATA_CENTER=01
SECRET_KEY=moengage-metrics-secret-key-2026
MAX_CAMPAIGN_PAGES=100
```

### Deployment Process

1. Push to GitHub main branch
2. Railway auto-deploys (connected to GitHub)
3. Build time: ~2-3 minutes
4. Health check: `/health` endpoint

### Monitoring

**Logs**: Available in Railway dashboard → Deploy Logs

**Key Log Messages**:
- `CREATING SEGMENTS FOR {date} to {date}`
- `FETCHING CAMPAIGN DATA FOR {date} to {date}`
- `METRICS CALCULATED SUCCESSFULLY`
- Campaign counts and API response codes

---

## 🔧 Troubleshooting

### Issue 1: Timeout Errors

**Symptoms**: 
- "Request timeout" message
- 504 Gateway Timeout
- Process killed after 5 minutes

**Causes**:
- Too many campaigns to fetch
- Slow API responses
- Network issues

**Solutions**:
1. Reduce `MAX_CAMPAIGN_PAGES` in config.py
2. Increase Gunicorn timeout in Procfile
3. Check Railway logs for specific API errors

---

### Issue 2: Zero Values in Metrics

**Symptoms**: All campaigns show 0 sent, 0 clicks, 0 opens

**Causes**:
- Wrong field names in Stats API parsing
- Date format mismatch
- API returning no data

**Solutions**:
1. Check logs for "performance_stats keys" to see available fields
2. Verify date format (YYYY-MM-DD)
3. Test with smaller date range

**Historical Fixes**:
- Changed `'opened'` to `'open'`
- Changed `'bounce'` to `'bounced'`
- Changed `'all_locales'` to `'all_locale'`

---

### Issue 3: Double Values

**Symptoms**: Metrics are exactly 2x expected values

**Cause**: Summing individual platforms (IOS, ANDROID) AND ALL_PLATFORMS

**Solution**: Use only `ALL_PLATFORMS` aggregate

---

### Issue 4: Session Expired

**Symptoms**: "Session expired. Please calculate metrics again."

**Causes**:
- Session timeout (2 hours)
- Cache file deleted
- Server restart

**Solutions**:
1. Recalculate metrics (data will be refetched)
2. Check if cache directory exists
3. Verify session configuration

---

### Issue 5: Wrong Date Range

**Symptoms**: Campaigns from wrong month appearing

**Cause**: Date format confusion (DD-MM-YYYY vs MM-DD-YYYY vs YYYY-MM-DD)

**Solution**: Always use YYYY-MM-DD (ISO format) for both APIs

**Historical Fix**: Changed Campaign Meta API from DD-MM-YYYY to YYYY-MM-DD

---

### Issue 6: Transactional Campaign Configuration

**Symptoms**: No transactional campaigns in results

**Cause**: `transactional_campaigns.json` is empty or missing

**Solution**:
1. Go to Settings page (`/settings`)
2. Add campaign IDs one by one
3. Or upload CSV with campaign IDs
4. Verify campaigns are EVENT_TRIGGERED type

---

## 📝 Configuration Files

### transactional_campaigns.json

**Format**:
```json
[
  {
    "campaign_id": "6986424d",
    "campaign_name": "Recipient added (UK)_Aspora",
    "channel": "EMAIL",
    "country": "UK"
  },
  {
    "campaign_id": "6986383",
    "campaign_name": "Aspora_payment completed_UK",
    "channel": "PUSH",
    "country": "UK"
  }
]
```

**Management**: Via Settings page (`/settings`)

**Validation**: 
- Campaign ID must exist in MoEngage
- Must be EVENT_TRIGGERED type (not ONE_TIME)
- Channel and country auto-detected from Campaign Meta API

---

## 🎓 Best Practices

### 1. Date Selection
- Use complete weeks for cleaner analysis
- Avoid partial days (start at 00:00, end at 23:59)
- Consider campaign scheduling patterns

### 2. Segment Count Entry
- Wait 30-60 seconds after segment creation for counts to stabilize
- Double-check counts before submitting
- Save counts externally for reference

### 3. Transactional Campaign Management
- Keep list updated as new campaigns launch
- Remove deprecated campaigns
- Use descriptive campaign names for easy identification

### 4. Performance Optimization
- Limit date range for faster processing
- Reduce `MAX_CAMPAIGN_PAGES` if timeouts occur
- Run during off-peak hours for better API response times

### 5. Data Validation
- Compare metrics with MoEngage dashboard
- Spot-check campaign counts in CSVs
- Verify segment counts match MoEngage UI

---

## 📞 Support & Maintenance

### Code Repository
GitHub: https://github.com/AnuragAtAspora/mtu-automation-web

### Deployment Platform
Railway: https://web-production-c1afd.up.railway.app/

### API Documentation
- MoEngage Segmentation API: https://docs.moengage.com/docs/segmentation-api
- MoEngage Campaign API: https://docs.moengage.com/docs/campaigns-api

### Key Contacts
- Workspace ID: 95PNUHBSYSLLJZ22PEOFMKF2
- Data Center: 01 (India)

---

## 🔄 Version History

### Current Version: 1.0
- 18 segments (9 per country)
- 6 metrics per country
- 8 campaign categories
- CSV export functionality
- Transactional campaign configuration
- File-based caching

### Recent Fixes
- Fixed `'open'` field name (was `'opened'`)
- Fixed double counting (use `ALL_PLATFORMS`)
- Fixed date format (use YYYY-MM-DD)
- Fixed CSV headers (Unique Opens/Clicks)
- Fixed transactional campaign date display

---

## 📚 Glossary

**Active User**: User with ORDER event (COMPLETED or PAYMENT_COMPLETED) in last 60 days

**Transacted User**: User with ORDER event in the selected analysis period

**Promotional Campaign**: ONE_TIME delivery type, sent once to a segment

**Transactional Campaign**: EVENT_TRIGGERED delivery type, sent when user performs an action

**Unique Opens**: Number of unique users who opened an email (not total open count)

**Unique Clicks**: Number of unique users who clicked (not total click count)

**CTR**: Click-Through Rate = (Unique Clicks / Total Sent) × 100

**Open Rate**: (Unique Opens / Total Sent) × 100

**ALL_PLATFORMS**: Aggregate stats across all platforms (IOS, ANDROID, UNKNOWN)

---

*Last Updated: February 9, 2026*
*Documentation Version: 1.0*
