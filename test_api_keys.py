#!/usr/bin/env python3
"""
Test different API keys with different endpoints
"""

import requests
import base64

def test_api_key(workspace_id, api_key, endpoint, description):
    """Test an API key with a specific endpoint"""
    
    auth_string = f"{workspace_id}:{api_key}"
    encoded_auth = base64.b64encode(auth_string.encode()).decode()
    
    headers = {
        'Authorization': f'Basic {encoded_auth}',
        'Content-Type': 'application/json',
        'MOE-APPKEY': workspace_id
    }
    
    print(f"\n{description}")
    print(f"Endpoint: {endpoint}")
    print(f"API Key: {api_key}")
    
    try:
        # Try POST with minimal payload
        response = requests.post(endpoint, headers=headers, json={}, timeout=10)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ SUCCESS - This API key works!")
        elif response.status_code == 400:
            print("⚠️  API key works, but request format needs adjustment")
        elif response.status_code == 401:
            print("❌ Authentication failed - wrong API key for this endpoint")
        elif response.status_code == 404:
            print("❌ Endpoint not found")
        else:
            print(f"Response: {response.text[:200]}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Connection error: {e}")

def main():
    print("MoEngage API Key Tester")
    print("=" * 40)
    
    workspace_id = "95PNUHBSYSLLJZ22PEOFMKF2"
    
    # You'll need to get these from your MoEngage dashboard
    print("Please provide your API keys from MoEngage Dashboard:")
    print("Go to Settings → Account → APIs")
    print()
    
    current_api_key = input("Enter your current API key (3XMHJ83D2X4V): ").strip() or "3XMHJ83D2X4V"
    
    print("\nIf you have additional API keys, enter them (press Enter to skip):")
    data_api_key = input("Data API Key: ").strip()
    campaign_api_key = input("Campaign Report API Key: ").strip()
    
    # Test endpoints
    endpoints = [
        ("https://api-01.moengage.com/v1/campaigns/stats", "Campaign Stats API"),
        ("https://api-01.moengage.com/v1/segments", "Custom Segments API"),
    ]
    
    api_keys_to_test = [
        (current_api_key, "Current API Key"),
    ]
    
    if data_api_key:
        api_keys_to_test.append((data_api_key, "Data API Key"))
    if campaign_api_key:
        api_keys_to_test.append((campaign_api_key, "Campaign Report API Key"))
    
    # Test each API key with each endpoint
    for endpoint, endpoint_name in endpoints:
        print(f"\n{'='*50}")
        print(f"Testing {endpoint_name}")
        print('='*50)
        
        for api_key, key_name in api_keys_to_test:
            test_api_key(workspace_id, api_key, endpoint, f"{key_name} with {endpoint_name}")

if __name__ == "__main__":
    main()