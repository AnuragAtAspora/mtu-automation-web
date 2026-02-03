#!/usr/bin/env python3
"""
Guide and helper for creating dynamic MoEngage reports
"""

from datetime import datetime, timedelta

def generate_report_names(start_date, end_date):
    """Generate standardized report names for a date range"""
    
    start_dt = datetime.strptime(start_date, '%Y-%m-%d')
    end_dt = datetime.strptime(end_date, '%Y-%m-%d')
    
    # Create readable date range string
    if start_dt.month == end_dt.month and start_dt.year == end_dt.year:
        if start_dt.day == 1 and end_dt.day == 31:
            # Full month
            date_suffix = f"{start_dt.strftime('%b%Y')}"  # Jan2026
        else:
            # Partial month
            date_suffix = f"{start_dt.strftime('%b%d')}-{end_dt.strftime('%d_%Y')}"  # Jan01-15_2026
    else:
        # Cross-month
        date_suffix = f"{start_dt.strftime('%b%d')}-{end_dt.strftime('%b%d_%Y')}"  # Jan15-Feb15_2026
    
    reports = {
        'transactional_pn': f"API_TX_PN_{date_suffix}",
        'transactional_email': f"API_TX_Email_{date_suffix}",
        'promotional_pn': f"API_PR_PN_{date_suffix}",
        'promotional_email': f"API_PR_Email_{date_suffix}"
    }
    
    return reports

def create_moengage_report_instructions(start_date, end_date):
    """Generate step-by-step instructions for creating reports in MoEngage dashboard"""
    
    reports = generate_report_names(start_date, end_date)
    
    instructions = f"""
🔧 CREATING DYNAMIC MOENGAGE REPORTS FOR {start_date} TO {end_date}
{'='*70}

Since the MoEngage Reports API doesn't support dynamic date filtering, you need to 
create new reports in the MoEngage dashboard with the correct date ranges.

📋 STEP-BY-STEP INSTRUCTIONS:

1. 🌐 LOGIN TO MOENGAGE DASHBOARD
   - Go to your MoEngage dashboard
   - Navigate to: Engage → Campaigns

2. 📊 CREATE EXPORT REPORTS
   - Click "Export" in the header
   - Select "Advanced" (for API access)

3. 🎯 CREATE 4 SEPARATE REPORTS:

   Report 1: TRANSACTIONAL PUSH NOTIFICATIONS
   ----------------------------------------
   - Report Name: {reports['transactional_pn']}
   - Campaign Type: Push Notifications
   - Campaign Filter: Transactional campaigns only
   - Date Range: {start_date} to {end_date}
   - Delivery Method: REST API
   - Include Fields: Campaign Name, All Platform Sent, Android Sent, iOS Sent

   Report 2: TRANSACTIONAL EMAILS
   ------------------------------
   - Report Name: {reports['transactional_email']}
   - Campaign Type: Email
   - Campaign Filter: Transactional campaigns only
   - Date Range: {start_date} to {end_date}
   - Delivery Method: REST API
   - Include Fields: Campaign Name, Sent, Total Open

   Report 3: PROMOTIONAL PUSH NOTIFICATIONS
   ----------------------------------------
   - Report Name: {reports['promotional_pn']}
   - Campaign Type: Push Notifications
   - Campaign Filter: Promotional campaigns only
   - Date Range: {start_date} to {end_date}
   - Delivery Method: REST API
   - Include Fields: Campaign Name, All Platform Sent, Android Sent, iOS Sent

   Report 4: PROMOTIONAL EMAILS
   ----------------------------
   - Report Name: {reports['promotional_email']}
   - Campaign Type: Email
   - Campaign Filter: Promotional campaigns only
   - Date Range: {start_date} to {end_date}
   - Delivery Method: REST API
   - Include Fields: Campaign Name, Sent

4. ⚙️ UPDATE CODE CONFIGURATION
   Once reports are created, update the report filenames in the code:

   ```python
   reports = {{
       'transactional_pn': "{reports['transactional_pn']}",
       'transactional_email': "{reports['transactional_email']}",
       'promotional_pn': "{reports['promotional_pn']}",
       'promotional_email': "{reports['promotional_email']}"
   }}
   ```

5. 🧪 TEST THE NEW REPORTS
   Run the Communications Per User calculator to verify the new reports work correctly.

💡 TIPS:
- Reports may take a few minutes to generate after creation
- Make sure to select "REST API" as delivery method
- Use consistent naming convention for easy identification
- Test with a small date range first to verify setup

🎯 EXPECTED RESULTS:
With properly configured reports for {start_date} to {end_date}, you should get:
- Accurate communication counts for the exact period
- Proper country filtering (UK/UAE campaigns)
- Real-time data that matches your manual calculations

📞 SUPPORT:
If you encounter issues creating reports, contact MoEngage support and mention:
- You need API access for campaign reports
- You want to create reports with specific date ranges
- You're using the Campaign Report API endpoint
"""
    
    return instructions, reports

def main():
    print("🔧 DYNAMIC MOENGAGE REPORTS HELPER")
    print("=" * 50)
    
    # Example: January 2026
    start_date = "2026-01-01"
    end_date = "2026-01-31"
    
    instructions, reports = create_moengage_report_instructions(start_date, end_date)
    
    print(instructions)
    
    print(f"\n📝 GENERATED REPORT NAMES:")
    for report_type, name in reports.items():
        print(f"  {report_type}: {name}")
    
    print(f"\n🔄 TO USE DIFFERENT DATE RANGES:")
    print(f"Run this script with different start_date and end_date values")
    print(f"to generate instructions for other periods.")

if __name__ == "__main__":
    main()