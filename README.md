# MoEngage Metrics Calculator

Clean, modular web application for calculating MoEngage communication metrics.

## Features

- Select date range
- Create 16 segments in MoEngage (Combined Android/iOS)
- Enter segment counts from MoEngage dashboard
- Fetch campaign data and calculate metrics

## Metrics Calculated

- Communications per user (Transactional & Promotional)
- MTU (Monthly Transacting Users) %
- Delivery rates (Push & Email)
- Engagement rates (CTR & Open Rate)
- Unsubscribe rates

## Project Structure

```
/
├── app.py                      # Flask application
├── config.py                   # Configuration
├── requirements.txt            # Dependencies
├── Procfile                    # Railway deployment
├── runtime.txt                 # Python version
├── modules/
│   ├── __init__.py
│   ├── segment_creator.py     # Segmentation API
│   ├── campaign_fetcher.py    # Stats + Meta API
│   └── metrics_calculator.py  # Metrics logic
└── templates/
    ├── base.html
    ├── index.html
    ├── segments_created.html
    └── results.html
```

## Setup

### Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables
export MOENGAGE_WORKSPACE_ID="your_workspace_id"
export MOENGAGE_DATA_API_KEY="your_data_api_key"
export MOENGAGE_CAMPAIGN_API_KEY="your_campaign_api_key"
export MOENGAGE_DATA_CENTER="01"
export SECRET_KEY="your_secret_key"

# Run
python app.py
```

Visit: http://localhost:5000

### Deploy to Railway

```bash
git add .
git commit -m "Deploy"
git push origin main
```

Set environment variables in Railway dashboard.

## Flow

1. **Select dates** → Click "Create Segments"
2. **16 segments created** in MoEngage (~2-3 min)
3. **Open each segment** → Note counts
4. **Enter counts** → Click "Calculate Metrics"
5. **Campaign data fetched** (~3-4 min)
6. **Metrics displayed**

## Configuration

Edit `config.py`:
- `API_TIMEOUT`: 60 seconds
- `RATE_LIMIT_DELAY`: 1 second
- `MAX_CAMPAIGN_PAGES`: 50 pages

## Segments Created

**16 segments total** (8 UK + 8 UAE):
1. All Users
2. Active Users (60d)
3. Received Push (Combined Android/iOS)
4. Received Email
5. Active + Received Push
6. Active + Received Email
7. Unsubscribed Push
8. Unsubscribed Email

Push segments use OR logic: `NOTIFICATION_RECEIVED_MOE` OR `n_i_s`

## License

MIT
