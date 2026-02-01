#!/usr/bin/env python3
"""
Test MoEngage Report API with the provided secret key
"""

import requests
import base64
import hashlib
import hmac
from config import MOENGAGE_APP_ID, CAMPAIGN_API_KEY, DATA_CENTER

def generate_signature(workspace_id, filename, secret_key):
    """Generate signature as per MoEngage documentation"""
    # Format: WORKSPACE_ID + FILENAME + SECRET_KEY
    message = f"{workspace_id}{filename}{secret_key}"
    
    # Using HMAC-SHA256
    signature = hmac.new(
        secret_key.encode('utf-8'),
        message.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()
    
    return signature

def test_report_download():
    """Test report download with correct signature"""
    
    filename = "API_Test_PN_report_20260128"
    secret_key = "3XMHJ83D2X4V"  # Your provided secret key
    
    # Generate signature
    signature = generate_signature(MOENGAGE_APP_ID, filename, secret_key)
    
    # URL
    url = f"https://api-{DATA_CENTER}.moengage.com/campaign_reports/rest_api/{MOENGAGE_APP_ID}/{filename}"
    
    # Headers with Basic Auth
    auth_string = f"{MOENGAGE_APP_ID}:{CAMPAIGN_API_KEY}"
    encoded_auth = base64.b64encode(auth_string.encode()).decode()
    
    headers = {
        'Authorization': f'Basic {encoded_auth}',
        'MOE-APPKEY': MOENGAGE_APP_ID
    }
    
    # Parameters
    params = {'signature': signature}
    
    print("MoEngage Report Download Test")
    print("=" * 40)
    print(f"Workspace ID: {MOENGAGE_APP_ID}")
    print(f"Filename: {filename}")
    print(f"Secret Key: {secret_key}")
    print(f"Message: {MOENGAGE_APP_ID}{filename}{secret_key}")
    print(f"Signature: {signature}")
    print(f"URL: {url}")
    print()
    
    try:
        print("Downloading report...")
        response = requests.get(url, headers=headers, params=params, timeout=30)
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ SUCCESS! Report downloaded successfully!")
            
            # Check content type
            content_type = response.headers.get('content-type', 'unknown')
            print(f"Content Type: {content_type}")
            print(f"Content Length: {len(response.text)} characters")
            
            # Show first few lines if it looks like CSV
            if response.text:
                lines = response.text.split('\n')
                print(f"\nFirst 5 lines of report:")
                for i, line in enumerate(lines[:5], 1):
                    print(f"{i}: {line}")
                
                # Save to file for inspection
                with open('downloaded_report.csv', 'w') as f:
                    f.write(response.text)
                print(f"\n📁 Report saved as 'downloaded_report.csv'")
                
                return response.text
            else:
                print("⚠️  Empty response received")
                
        elif response.status_code == 400:
            print("❌ Bad Request")
            print(f"Response: {response.text}")
            
        elif response.status_code == 401:
            print("❌ Authentication failed")
            print(f"Response: {response.text}")
            
        elif response.status_code == 404:
            print("❌ Report not found")
            print("This might mean:")
            print("- Report hasn't been generated yet")
            print("- Filename is incorrect")
            print("- Report has expired (7 days)")
            
        else:
            print(f"❌ Error {response.status_code}")
            print(f"Response: {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"💥 Connection error: {e}")
    
    return None

if __name__ == "__main__":
    result = test_report_download()
    
    if result:
        print("\n🎉 SUCCESS! We can now build the full automation.")
    else:
        print("\n❌ Still having issues. May need to check report configuration.")