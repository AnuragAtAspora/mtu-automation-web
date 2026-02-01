# MoEngage Data Export API Setup Guide

## Overview
The Data Export API integration provides real-time user metrics and campaign interaction data through webhook streams.

## Components Created

### 1. Webhook Server (`webhook_server.py`)
- **Purpose**: Receives real-time events from MoEngage
- **Database**: SQLite database to store events and user metrics
- **Endpoints**:
  - `POST /moengage/webhook` - Receives MoEngage events
  - `GET /metrics/users/<date>` - Get user metrics for specific date
  - `GET /metrics/range` - Get metrics for date range
  - `GET /health` - Health check

### 2. Integrated Automation (`data_export_integration.py`)
- **Purpose**: Combines Campaign Reports API + Data Export API
- **Features**:
  - Auto-detects user counts from webhook data
  - Falls back to campaign reports if needed
  - Comprehensive metrics calculation
  - Google Sheets integration

## Setup Steps

### Step 1: Install Dependencies
```bash
pip install flask sqlite3
```

### Step 2: Start Webhook Server
```bash
python3 webhook_server.py
```
Server will run on: `http://localhost:5000`

### Step 3: Configure MoEngage Data Export

1. **Go to MoEngage Dashboard**
2. **Navigate to**: Settings → Data Export → Streams
3. **Create New Stream**:
   - **Name**: "Automation Webhook"
   - **Destination Type**: API Endpoint
   - **Endpoint URL**: `http://your-server.com:5000/moengage/webhook`
   - **Method**: POST
   - **Content Type**: application/json

4. **Select Events to Export**:
   - ✅ Campaign Events (Push, Email, In-App)
   - ✅ User Events (if needed)
   - ✅ Custom Events (if needed)

5. **Configure Authentication** (if required):
   - Add any headers or authentication your server needs

### Step 4: Test Webhook
```bash
# Check if webhook is receiving data
curl http://localhost:5000/health

# Check user metrics (after some data is received)
curl http://localhost:5000/metrics/users/2026-01-28
```

### Step 5: Run Integrated Automation
```bash
python3 data_export_integration.py
```

## Data Flow

```
MoEngage → Webhook Server → SQLite Database
                ↓
    Integrated Automation Script
                ↓
         Google Sheets
```

## Benefits of Integration

### Data Export API Provides:
- ✅ **Real-time user counts** (no manual input needed)
- ✅ **Active user metrics** (daily/monthly active users)
- ✅ **Campaign interaction data** (opens, clicks, etc.)
- ✅ **User segmentation data** (email users, push users)

### Campaign Reports API Provides:
- ✅ **Accurate send counts** (emails sent, push sent)
- ✅ **Campaign performance data**
- ✅ **Historical data** (for past periods)

## Usage Scenarios

### Scenario 1: Real-time Monitoring
- Webhook server runs continuously
- Receives events as they happen
- Provides up-to-date user metrics

### Scenario 2: Historical Analysis
- Use Campaign Reports API for past data
- Use Data Export API for current user counts
- Combine both for comprehensive metrics

### Scenario 3: Automated Reporting
- Run integrated automation daily/weekly
- Auto-detects user counts from webhook data
- Falls back to manual input if needed

## Troubleshooting

### Webhook Not Receiving Data
1. Check MoEngage Stream configuration
2. Verify endpoint URL is accessible
3. Check server logs for errors

### Database Issues
1. Check if `moengage_data.db` file exists
2. Verify SQLite permissions
3. Check database schema

### Missing User Metrics
1. Ensure webhook has been running for some time
2. Check if events are being processed
3. Verify date format in queries

## Next Steps

1. **Deploy webhook server** to a public server (not localhost)
2. **Configure MoEngage Stream** with your public webhook URL
3. **Test the integration** with real data
4. **Set up monitoring** for the webhook server
5. **Schedule automated runs** of the integrated automation

## Security Considerations

- Use HTTPS for webhook endpoints in production
- Add authentication to webhook endpoint if needed
- Secure your database file
- Monitor webhook server logs
- Rate limit webhook endpoint if necessary