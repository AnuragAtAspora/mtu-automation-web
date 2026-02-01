#!/usr/bin/env python3
"""
Test all possible MoEngage API endpoint patterns
"""

import requests
import base64
from config import MOENGAGE_APP_ID, DATA_API_KEY, CAMPAIGN_API_KEY, DATA_CENTER

def test_endpoint_patterns():
    """Test different possible endpoint patterns"""
    
    # Different base URL patterns to try
    base_urls = [
        f"https://api-{DATA_CENTER}.moengage.com/v1",
        f"https://api-{DATA_CENTER}.moengage.com/v2", 
        f"https://api-{DATA_CENTER}.moengage.com",
        f"https://app-{DATA_CENTER}.moengage.com/v1",
        f"https://dashboard-{DATA_CENTER}.moengage.com/v1",
    ]
    
    # Different endpoint patterns to try
    endpoints = [
        "/campaigns/stats",
        "/stats", 
        "/segments",
        "/analytics/campaigns",
        "/reports/campaigns",
        "/api/campaigns/stats",
        "/api/v1/campaigns/stats",
    ]
    
    # Test with campaign API key
    auth_string = f"{MOENGAGE_APP_ID}:{CAMPAIGN_API_KEY}"
    encoded_auth = base64.b64encode(auth_string.encode()).decode()
    
    headers = {
        'Authorization': f'Basic {encoded_auth}',
        'Content-Type': 'application/json',
        'MOE-APPKEY': MOENGAGE_APP_ID
    }
    
    print("Testing different endpoint patterns...")
    print("=" * 50)
    
    for base_url in base_urls:
        print(f"\nTesting base URL: {base_url}")
        print("-" * 30)
        
        for endpoint in endpoints:
            full_url = base_url + endpoint
            
            try:
                response = requests.get(full_url, headers=headers, timeout=5)
                status = response.status_code
                
                if status == 200:
                    print(f"✅ {endpoint} - SUCCESS (200)")
                elif status == 401:
                    print(f"🔑 {endpoint} - Auth issue (401)")
                elif status == 405:
                    print(f"⚠️  {endpoint} - Method not allowed (405) - try POST")
                elif status == 404:
                    print(f"❌ {endpoint} - Not found (404)")
                else:
                    print(f"❓ {endpoint} - Status {status}")
                    
            except requests.exceptions.RequestException as e:
                print(f"💥 {endpoint} - Connection error")

def test_working_endpoint():
    """Test the transition endpoint that we know works"""
    
    auth_string = f"{MOENGAGE_APP_ID}:{DATA_API_KEY}"
    encoded_auth = base64.b64encode(auth_string.encode()).decode()
    
    headers = {
        'Authorization': f'Basic {encoded_auth}',
        'Content-Type': 'application/json',
        'MOE-APPKEY': MOENGAGE_APP_ID
    }
    
    url = f"https://api-{DATA_CENTER}.moengage.com/v1/transition/{MOENGAGE_APP_ID}"
    
    print(f"\n\nTesting known working endpoint:")
    print(f"URL: {url}")
    
    try:
        # Try with minimal valid payload
        payload = {
            "type": "transition",
            "elements": []
        }
        
        response = requests.post(url, headers=headers, json=payload, timeout=10)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text[:200]}...")
        
        if response.status_code == 200:
            print("✅ Data API key is working with transition endpoint!")
        elif response.status_code == 400:
            print("✅ Data API key works, just need correct payload format")
        
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")

def main():
    print("MoEngage Endpoint Discovery")
    print("=" * 40)
    print(f"Workspace ID: {MOENGAGE_APP_ID}")
    print(f"Data Center: {DATA_CENTER}")
    
    test_endpoint_patterns()
    test_working_endpoint()
    
    print("\n" + "=" * 50)
    print("RECOMMENDATION:")
    print("If no endpoints work, we should:")
    print("1. Use Campaign Report API (file download approach)")
    print("2. Contact MoEngage support to verify API access")
    print("3. Check if your account has API access enabled")

if __name__ == "__main__":
    main()