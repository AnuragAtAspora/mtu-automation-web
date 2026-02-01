"""
Configuration template for MoEngage automation
Copy this file to config.py and fill in your actual values
"""

# MoEngage Configuration
MOENGAGE_APP_ID = "your_moengage_app_id_here"  # Workspace ID from Settings -> Account -> APIs
MOENGAGE_API_KEY = "your_moengage_api_key_here"  # API Key from Settings -> Account -> APIs
DATA_CENTER = "01"  # Your MoEngage data center number (01, 02, 03, etc.)

# Google Sheets Configuration
GOOGLE_SHEET_ID = "your_google_sheet_id_here"  # Extract from sheet URL
GOOGLE_SHEET_NAME = "Metrics"  # Name of the worksheet tab

# Optional: Customize column headers for your sheet
SHEET_HEADERS = [
    "Period Start",
    "Period End", 
    "Email per User",
    "PN per User",
    "Total Emails Sent",
    "Total PN Sent",
    "Total Users"
]