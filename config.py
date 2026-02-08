"""
Configuration for MoEngage Metrics Application
"""
import os

# MoEngage API Configuration
MOENGAGE_CONFIG = {
    'workspace_id': os.environ.get('MOENGAGE_WORKSPACE_ID', '95PNUHBSYSLLJZ22PEOFMKF2'),
    'data_api_key': os.environ.get('MOENGAGE_DATA_API_KEY', 'Mj5JSGKcwYum9NKAGmGHJG_E'),
    'campaign_api_key': os.environ.get('MOENGAGE_CAMPAIGN_API_KEY', '3XMHJ83D2X4V'),
    'data_center': os.environ.get('MOENGAGE_DATA_CENTER', '01')
}

# Flask Configuration
SECRET_KEY = os.environ.get('SECRET_KEY', 'moengage-metrics-secret-key-2026')
DEBUG = os.environ.get('DEBUG', 'False').lower() == 'true'

# API Settings
API_TIMEOUT = 60  # seconds
RATE_LIMIT_DELAY = 1  # seconds between API calls
MAX_CAMPAIGN_PAGES = int(os.environ.get('MAX_CAMPAIGN_PAGES', '20'))  # Limit campaign fetch to prevent timeout (15 campaigns per page)
