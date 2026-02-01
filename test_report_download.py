#!/usr/bin/env python3
"""
Test MoEngage Campaign Report download with different approaches
"""

import requests
import base64
import hashlib
import hmac
from datetime import datetime
from config import MOENGAGE_APP_ID, CAMPAIGN_API_KEY, DATA_CENTER

def test_report_download_simple(filename):
    """Test report download without signature"""
    
    auth_string = f"{MOENGAGE_APP_ID}:{CAMPAIGN_API_KEY}"
    encoded_auth = base64.b64encode(auth_string.encode()).decode()
    
    headers = {
        'Authorization': f'Basic {encoded_auth}',
        'Content-Type': 'application/json',
        'MOE-APPKEY': MOENGAGE_APP_ID
    }
    
    # Try different possible endpoints
    endpoints = [
        f"https://api-{DATA_CENTER}.moengage.com/v1/reports/download/{MOENGAGE_APP_ID}/{filename}",
        f"https://api-{DATA_CENTER}.moengage.com/v1/reports/{filename}",
        f"https://api-{DATA_CENTER}.moengage.com/v1/export/{filename}",
        f"https://dashboard-{DATA_CENTER}.moengage.com/v1/reports/download/{MOENGAGE_APP_ID}/{filename}",
    ]
    
    print(f"Testing report download for: {filename}")
    print("=" * 50)
    
    for url in endpoints:
        print(f"\nTrying: {url}")
        
        try:
            response = requests.get(url, headers=headers, timeout=30)
            print(f"Status: {response.status_code}")
            
            if response.status_code == 200:
                print("✅ SUCCESS! Report downloaded")
                print(f"Content type: {response.headers.get('content-type', 'unknown')}")
                print(f"Content length: {len(response.text)} characters")
                print(f"First 200 chars: {response.text[:200]}...")
                return response.text
                
            elif response.status_code == 401:
                print("❌ Authentication failed")
                
            elif response.status_code == 404:
                print("❌ Report not found")
                
            elif response.status_code == 400:
                print("⚠️  Bad request - might need signature")
                print(f"Response: {response.text[:200]}")
                
            else:
                print(f"❓ Status {response.status_code}")
                print(f"Response: {response.text[:200]}")
                
        except requests.exceptions.RequestException as e:
            print(f"💥 Connection error: {e}")
    
    return None

def test_report_with_api_key_signature(filename):
    """Test using API key as secret for signature"""
    
    print(f"\n\nTesting with API key as signature secret...")
    print("=" * 50)
    
    # Generate signature using API key as secret
    message = f"{MOENGAGE_APP_ID}{filename}{CAMPAIGN_API_KEY}"
    signature = hmac.new(
        CAMPAIGN_API_KEY.encode('utf-8'),
        message.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()
    
    auth_string = f"{MOENGAGE_APP_ID}:{CAMPAIGN_API_KEY}"
    encoded_auth = base64.b64encode(auth_string.encode()).decode()
    
    headers = {
        'Authorization': f'Basic {encoded_auth}',
    }
    
    url = f"https://api-{DATA_CENTER}.moengage.com/v1/reports/download/{MOENGAGE_APP_ID}/{filename}"
    params = {'signature': signature}
    
    print(f"URL: {url}")
    print(f"Signature: {signature}")
    
    try:
        response = requests.get(url, headers=headers, params=params, timeout=30)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ SUCCESS with API key signature!")
            print(f"Content: {response.text[:200]}...")
            return response.text
        else:
            print(f"Response: {response.text[:200]}")
            
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
    
    return None

def test_report_list():
    """Try to list available reports"""
    
    print(f"\n\nTrying to list available reports...")
    print("=" * 50)
    
    auth_string = f"{MOENGAGE_APP_ID}:{CAMPAIGN_API_KEY}"
    encoded_auth = base64.b64encode(auth_string.encode()).decode()
    
    headers = {
        'Authorization': f'Basic {encoded_auth}',
        'Content-Type': 'application/json',
        'MOE-APPKEY': MOENGAGE_APP_ID
    }
    
    endpoints = [
        f"https://api-{DATA_CENTER}.moengage.com/v1/reports",
        f"https://api-{DATA_CENTER}.moengage.com/v1/reports/list",
        f"https://api-{DATA_CENTER}.moengage.com/v1/export",
    ]
    
    for url in endpoints:
        print(f"\nTrying: {url}")
        
        try:
            response = requests.get(url, headers=headers, timeout=30)
            print(f"Status: {response.status_code}")
            
            if response.status_code == 200:
                print("✅ Got response!")
                print(f"Response: {response.text[:300]}...")
            elif response.status_code != 404:
                print(f"Response: {response.text[:200]}")
                
        except requests.exceptions.RequestException as e:
            print(f"Error: {e}")

def main():
    filename = "API_Test_PN_report_20260128"
    
    print("MoEngage Report Download Test")
    print("=" * 40)
    print(f"Workspace ID: {MOENGAGE_APP_ID}")
    print(f"Filename: {filename}")
    print(f"Data Center: {DATA_CENTER}")
    
    # Try different approaches
    result1 = test_report_download_simple(filename)
    result2 = test_report_with_api_key_signature(filename)
    test_report_list()
    
    if result1 or result2:
        print("\n🎉 SUCCESS! We found a working approach.")
    else:
        print("\n❌ No approach worked. Possible issues:")
        print("1. Report might not be generated yet")
        print("2. Different API endpoint structure")
        print("3. Need to trigger report generation first")
        print("4. Different authentication method")

if __name__ == "__main__":
    main()