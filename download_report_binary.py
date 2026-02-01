#!/usr/bin/env python3
"""
Download MoEngage report with proper binary handling
"""

import requests
import base64
import hashlib
import zipfile
import io
from config import MOENGAGE_APP_ID, CAMPAIGN_API_KEY, DATA_CENTER

def download_report_properly():
    """Download report with proper binary handling"""
    
    filename = "API_Test_PN_report_20260128"
    secret_key = CAMPAIGN_API_KEY  # 3XMHJ83D2X4V
    
    # Generate signature with correct format
    signature_key = f"{MOENGAGE_APP_ID}|{filename}|{secret_key}"
    signature = hashlib.sha256(signature_key.encode('utf-8')).hexdigest()
    
    url = f"https://api-{DATA_CENTER}.moengage.com/campaign_reports/rest_api/{MOENGAGE_APP_ID}/{filename}"
    
    # Headers
    auth_string = f"{MOENGAGE_APP_ID}:{CAMPAIGN_API_KEY}"
    encoded_auth = base64.b64encode(auth_string.encode()).decode()
    
    headers = {
        'Authorization': f'Basic {encoded_auth}',
        'MOE-APPKEY': MOENGAGE_APP_ID,
        'Signature': signature
    }
    
    print("Downloading MoEngage Report (Binary Mode)")
    print("=" * 40)
    print(f"URL: {url}")
    print(f"Signature: {signature}")
    print()
    
    try:
        # Download in binary mode
        response = requests.get(url, headers=headers, timeout=30)
        
        if response.status_code == 200:
            print("✅ Report downloaded successfully!")
            
            # Save as ZIP file
            with open('report.zip', 'wb') as f:
                f.write(response.content)
            
            print(f"📁 Saved as report.zip ({len(response.content)} bytes)")
            
            # Extract and read CSV
            try:
                with zipfile.ZipFile('report.zip', 'r') as zip_file:
                    file_list = zip_file.namelist()
                    print(f"Files in ZIP: {file_list}")
                    
                    # Extract all files
                    zip_file.extractall('extracted_reports')
                    print("📂 Extracted to 'extracted_reports' folder")
                    
                    # Read the CSV file
                    csv_files = [f for f in file_list if f.endswith('.csv')]
                    if csv_files:
                        csv_filename = csv_files[0]
                        with zip_file.open(csv_filename) as csv_file:
                            csv_content = csv_file.read().decode('utf-8')
                            
                        print(f"\n📊 CSV Content from {csv_filename}:")
                        print("-" * 50)
                        lines = csv_content.split('\n')[:10]  # First 10 lines
                        for i, line in enumerate(lines, 1):
                            print(f"{i:2}: {line}")
                        
                        # Save clean CSV
                        with open('clean_report.csv', 'w') as f:
                            f.write(csv_content)
                        print(f"\n📄 Clean CSV saved as 'clean_report.csv'")
                        
                        return csv_content
                    else:
                        print("❌ No CSV files found in ZIP")
                        
            except zipfile.BadZipFile:
                print("❌ Invalid ZIP file")
                
        else:
            print(f"❌ Error {response.status_code}: {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"💥 Connection error: {e}")
    
    return None

if __name__ == "__main__":
    csv_content = download_report_properly()
    
    if csv_content:
        print("\n🎉 SUCCESS! We now have the CSV data and can build the automation.")
    else:
        print("\n❌ Failed to extract CSV content.")