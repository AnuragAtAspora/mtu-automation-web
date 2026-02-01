# Google Sheets Setup Guide

## Step 1: Create Google Service Account

1. **Go to Google Cloud Console**: https://console.cloud.google.com/
2. **Create or Select Project**:
   - Click "Select a project" → "New Project"
   - Name it "MoEngage Automation" → Create

3. **Enable APIs**:
   - Go to "APIs & Services" → "Library"
   - Search and enable: "Google Sheets API"
   - Search and enable: "Google Drive API"

4. **Create Service Account**:
   - Go to "APIs & Services" → "Credentials"
   - Click "Create Credentials" → "Service Account"
   - Name: "moengage-automation"
   - Click "Create and Continue"
   - Skip roles for now → "Done"

5. **Download Credentials**:
   - Click on the service account you just created
   - Go to "Keys" tab
   - Click "Add Key" → "Create New Key"
   - Choose "JSON" → Create
   - **Save this file as `google_credentials.json` in your project folder**

## Step 2: Create Google Sheet

1. **Create New Sheet**: https://sheets.google.com
2. **Name it**: "MoEngage Metrics" (or whatever you prefer)
3. **Set up headers** in Row 1:
   ```
   A1: Period Start
   B1: Period End  
   C1: Email per User
   D1: Push per User
   E1: Total Emails Sent
   F1: Total Push Sent
   G1: Total Users
   H1: Total Campaigns
   ```

## Step 3: Share Sheet with Service Account

1. **Open your Google Sheet**
2. **Click "Share" button**
3. **Copy the service account email** from the JSON file (looks like: `moengage-automation@your-project.iam.gserviceaccount.com`)
4. **Paste it in the share dialog**
5. **Give "Editor" permissions**
6. **Click "Send"**

## Step 4: Get Sheet ID

From your Google Sheet URL:
```
https://docs.google.com/spreadsheets/d/1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms/edit
```

The Sheet ID is: `1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms`

**Copy this ID - I'll need it for the script.**