# MTU Automation Setup Guide

## Overview
The MTU (Marketing Touch Users) automation calculates the percentage of user base receiving communications based on the MTU method requirements.

## What's Been Created

### 1. MTU Automation Script (`mtu_automation.py`)
- **Purpose**: Main automation script for MTU calculations
- **Features**:
  - Calculates MTU metrics for UK and UAE
  - Handles both "all users" and "60-day active users" scenarios
  - Integrates with Data Export API webhook data
  - Updates Google Sheets automatically

### 2. Google Sheets Integration
- **New Tab**: "MTU Metrics" created in your existing Google Sheet
- **22 Columns** tracking all required MTU metrics
- **Sample Data**: Added for testing

### 3. Test Setup Script (`test_mtu_setup.py`)
- **Purpose**: Sets up and tests the Google Sheets integration
- **Status**: ✅ Successfully completed

## MTU Metrics Calculated

### For Both UK (GB) and UAE (AE):

#### 1. All Users Metrics
- **Push Notifications**: % of total user base who received ≥1 PN in period
- **Email**: % of total user base who received ≥1 Email in period

#### 2. Active Users Metrics (60-day)
- **Push Notifications**: % of 60-day active users who received ≥1 PN
- **Email**: % of 60-day active users who received ≥1 Email

## Prerequisites

### 1. Webhook Server Running
```bash
python3 webhook_server.py
```
The MTU automation requires webhook data to calculate metrics.

### 2. MoEngage Stream Configured
- Stream should be sending events to your webhook server
- Events must include country attributes ('GB' for UK, 'AE' for UAE)
- Transaction events needed for active user identification

## Usage

### Run MTU Automation
```bash
python3 mtu_automation.py
```

**Input Required:**
- End date (YYYY-MM-DD format)
- Must not exceed current date-1
- Period automatically starts from month beginning

**Example:**
```
End date (YYYY-MM-DD): 2026-01-27
```
This calculates metrics from 2026-01-01 to 2026-01-27.

## Google Sheets Output

### MTU Metrics Tab Columns:
1. **Period Start** - Start of calculation period
2. **Period End** - End of calculation period
3. **UK Total Users** - Total UK user base
4. **UK Active Users (60d)** - UK users who transacted in last 60 days
5. **UK Push All Users** - UK users who received ≥1 PN (count)
6. **UK Push All %** - UK users who received ≥1 PN (percentage)
7. **UK Push Active Users** - Active UK users who received ≥1 PN (count)
8. **UK Push Active %** - Active UK users who received ≥1 PN (percentage)
9. **UK Email All Users** - UK users who received ≥1 Email (count)
10. **UK Email All %** - UK users who received ≥1 Email (percentage)
11. **UK Email Active Users** - Active UK users who received ≥1 Email (count)
12. **UK Email Active %** - Active UK users who received ≥1 Email (percentage)
13-22. **UAE Metrics** - Same structure as UK but for UAE

## Data Requirements

### Webhook Events Must Include:
- **User ID** (`uid`)
- **Event Time** (`event_time`)
- **Campaign Channel** (`campaign_channel`) - containing 'push' or 'email'
- **Country Attribute** in `user_attributes` JSON:
  ```json
  {
    "user_attributes": {
      "country": "GB"  // or "AE"
    }
  }
  ```
- **Transaction Events** for active user identification

### Sample Event Structure:
```json
{
  "uid": "user123",
  "event_time": 1706400000,
  "campaign_channel": "push_notification",
  "user_attributes": {
    "country": "GB"
  },
  "event_name": "campaign_delivered"
}
```

## Troubleshooting

### No Webhook Data
```
❌ No webhook data available
```
**Solutions:**
1. Start webhook server: `python3 webhook_server.py`
2. Check MoEngage Stream configuration
3. Verify events are being received

### Missing Country Data
```
⚠️ Low user counts for UK/UAE
```
**Solutions:**
1. Verify country attributes in MoEngage user profiles
2. Check webhook events include country data
3. Ensure country values are 'GB' and 'AE'

### No Transaction Events
```
⚠️ No active users found
```
**Solutions:**
1. Verify transaction events are being sent to webhook
2. Check event names contain 'transaction'
3. Ensure transaction events have country attributes

## Next Steps

1. **Start Webhook Server** (if not running):
   ```bash
   python3 webhook_server.py
   ```

2. **Configure MoEngage Stream** to send events to webhook

3. **Test MTU Automation**:
   ```bash
   python3 mtu_automation.py
   ```

4. **Schedule Regular Runs** (optional):
   - Daily/weekly automation
   - Cron job setup
   - Automated reporting

## Integration with Existing Automation

- **Original automation** continues to use "Sheet1" tab
- **MTU automation** uses "MTU Metrics" tab
- **Both can run independently** or together
- **Same Google Sheet** - organized in separate tabs

## Sample Output

```
🚀 Starting MTU Automation
📅 Period: 2026-01-01 to 2026-01-27
✅ Found 15,432 events in webhook database

📊 Processing UK (GB)...
   Total user base: 50,000
   Active users (60d): 30,000
   Push users (all): 15,000 (30.00%)
   Push users (60d active): 9,000 (30.00%)
   Email users (all): 12,000 (24.00%)
   Email users (60d active): 7,200 (24.00%)

📊 Processing UAE (AE)...
   Total user base: 75,000
   Active users (60d): 45,000
   Push users (all): 22,500 (30.00%)
   Push users (60d active): 13,500 (30.00%)
   Email users (all): 18,000 (24.00%)
   Email users (60d active): 10,800 (24.00%)

✅ Successfully updated MTU Metrics sheet!
🎉 MTU automation completed successfully!
```