#!/usr/bin/env python3
"""
Test MoEngage Report API with additional parameters
"""

import requests
import base64
import hashlib
import hmac
from datetime import datetime, timedelta
from config import MOENGAGE_APP_ID, CAMPAIGN_API_KEY, DATA_CENTER

def test_with_additional_params():
    """Test report API with additional parameters that might be required"""
    
    filename = "API_Test_PN_report_20260128"
    secret_key = "3XMHJ83D2X4V"
    
    # Generate signature
    message = f"{MOENGAGE_APP_ID}{filename}{secret_key}"
    signature = hmac.new(
        secret_key.encode('utf-8'),
        message.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()
    
    # URL
    url = f"https://api-{DATA_CENTER}.moengage.com/campaign_reports/rest_api/{MOENGAGE_APP_ID}/{filename}"
    
    # Headers
    auth_string = f"{MOENGAGE_APP_ID}:{CAMPAIGN_API_KEY}"
    encoded_auth = base64.b64encode(auth_string.encode()).decode()
    
    headers = {
        'Authorization': f'Basic {encoded_auth}',
        'MOE-APPKEY': MOENGAGE_APP_ID
    }
    
    # Try different parameter combinations
    param_combinations = [
        # Basic signature only
        {'signature': signature},
        
        # With date range (maybe required)
        {
            'signature': signature,
            'from_date': '2026-01-01',
            'to_date': '2026-01-27'
        },
        
        # With app_id parameter
        {
            'signature': signature,
            'app_id': MOENGAGE_APP_ID
        },
        
        # With both
        {
            'signature': signature,
            'app_id': MOENGAGE_APP_ID,
            'from_date': '2026-01-01',
            'to_date': '2026-01-27'
        },
        
        # With filename in params
        {
            'signature': signature,
            'filename': filename
        },
        
        # All parameters
        {
            'signature': signature,
            'app_id': MOENGAGE_APP_ID,
            'filename': filename,
            'from_date': '2026-01-01',
            'to_date': '2026-01-27'
        }
    ]
    
    print("Testing MoEngage Report API with Additional Parameters")
    print("=" * 60)
    print(f"URL: {url}")
    print(f"Signature: {signature}")
    print()
    
    for i, params in enumerate(param_combinations, 1):
        print(f"{i}. Testing with parameters: {list(params.keys())}")
        print(f"   Params: {params}")
        
        try:
            response = requests.get(url, headers=headers, params=params, timeout=30)
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                print("   ✅ SUCCESS!")
                print(f"   Content length: {len(response.text)}")
                lines = response.text.split('\n')[:3]
                print("   First 3 lines:")
                for line in lines:
                    print(f"     {line}")
                return response.text
                
            elif response.status_code == 400:
                error_text = response.text
                print(f"   ❌ Bad Request: {error_text}")
                
                # Check if it's a different error than signature
                if "SIGNATURE" not in error_text:
                    print("   ⚠️  Different error - might be progress!")
                    
            else:
                print(f"   ❌ Status {response.status_code}: {response.text[:100]}")
                
        except requests.exceptions.RequestException as e:
            print(f"   💥 Error: {e}")
        
        print()
    
    return None

def test_report_generation_trigger():
    """Try to trigger report generation first"""
    
    print("Attempting to trigger report generation...")
    print("-" * 40)
    
    # Sometimes reports need to be triggered before download
    # Try different possible trigger endpoints
    trigger_urls = [
        f"https://api-{DATA_CENTER}.moengage.com/campaign_reports/generate/{MOENGAGE_APP_ID}/API_Test_PN_report_20260128",
        f"https://api-{DATA_CENTER}.moengage.com/v1/reports/generate/{MOENGAGE_APP_ID}/API_Test_PN_report_20260128",
        f"https://api-{DATA_CENTER}.moengage.com/reports/trigger/{MOENGAGE_APP_ID}/API_Test_PN_report_20260128"
    ]
    
    auth_string = f"{MOENGAGE_APP_ID}:{CAMPAIGN_API_KEY}"
    encoded_auth = base64.b64encode(auth_string.encode()).decode()
    
    headers = {
        'Authorization': f'Basic {encoded_auth}',
        'MOE-APPKEY': MOENGAGE_APP_ID,
        'Content-Type': 'application/json'
    }
    
    for url in trigger_urls:
        print(f"Trying: {url}")
        
        try:
            # Try POST to trigger
            response = requests.post(url, headers=headers, json={}, timeout=30)
            print(f"Status: {response.status_code}")
            
            if response.status_code in [200, 201, 202]:
                print("✅ Trigger might have worked!")
                print(f"Response: {response.text[:200]}")
                return True
            elif response.status_code != 404:
                print(f"Response: {response.text[:200]}")
                
        except requests.exceptions.RequestException as e:
            print(f"Error: {e}")
    
    return False

def main():
    # First try to trigger report generation
    triggered = test_report_generation_trigger()
    
    if triggered:
        print("\nWaiting 5 seconds for report generation...")
        import time
        time.sleep(5)
    
    # Then try to download with different parameters
    result = test_with_additional_params()
    
    if result:
        print("🎉 SUCCESS! Found working approach.")
    else:
        print("❌ Still not working. Recommendations:")
        print("1. Check if report exists in MoEngage dashboard")
        print("2. Verify report is configured for REST API delivery")
        print("3. Contact MoEngage support for correct API format")

if __name__ == "__main__":
    main()