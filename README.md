# MoEngage Google Sheets Automation

Automates fetching "Comms received per user" metrics from MoEngage and updating Google Sheets.

## Metrics Calculated

**Comms received per user** for a selected time period (month start to chosen date):
- **Email per user**: Total emails sent ÷ Total user base
- **PN per user**: Total push notifications sent ÷ Total user base

## Setup Instructions

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. MoEngage API Setup
1. Get your MoEngage credentials from MoEngage dashboard:
   - Go to Settings → Account → APIs
   - Copy **Workspace ID** (this is your APP_ID)
   - Copy **API Key** from the Campaign report/Business events section
   - Find your **Data Center number** from the [DC mapping page](https://developers.moengage.com/hc/en-us/articles/4404674776724-Overview)
2. Copy `config_template.py` to `config.py`
3. Fill in your MoEngage credentials in `config.py`

### 3. Google Sheets API Setup
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Enable Google Sheets API and Google Drive API
4. Create a Service Account:
   - Go to IAM & Admin > Service Accounts
   - Click "Create Service Account"
   - Download the JSON credentials file
   - Rename it to `google_credentials.json` and place in project folder
5. Share your Google Sheet with the service account email (found in the JSON file)
6. Get your Google Sheet ID from the URL and add to `config.py`

### 4. Run the Automation
```bash
python moengage_automation.py
```

## Usage

1. Run the script
2. Enter the end date (YYYY-MM-DD format)
   - Must be between month start and yesterday
   - Example: If today is Jan 27, you can choose Jan 1 to Jan 26
3. Script will:
   - Fetch email and PN sent counts from MoEngage
   - Get total user base as of end date
   - Calculate metrics
   - Display results
   - Optionally update Google Sheet

## Next Steps

This foundation supports one metric. We can easily extend it to:
- Add more metrics
- Schedule automatic runs
- Add data validation
- Customize Google Sheet formatting
- Add error handling and logging

## API Endpoints Used

The script uses these MoEngage API endpoints:
- **Stats API**: `POST https://api-0X.moengage.com/v1/stats` - Gets email and push notification sent counts
- **Custom Segment API**: `POST https://api-0X.moengage.com/v1/segments` - Creates temporary segment to get user count

**Authentication**: Uses Basic Authentication with Base64 encoded `workspace_id:api_key`

**Note**: Replace 'X' in URLs with your MoEngage data center number.