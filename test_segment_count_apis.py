#!/usr/bin/env python3
"""
Test various MoEngage APIs to see if we can get segment counts
"""

import requests
import base64
import json

# Configuration
WORKSPACE_ID = "95PNUHBSYSLLJZ22PEOFMKF2"
DATA_API_KEY = "Mj5JSGKcwYum9NKAGmGHJG_E"
CAMPAIGN_API_KEY = "3XMHJ83D2X4V"
DATA_CENTER = "01"

def test_segment_analytics_api():
    """Test if there's a segment analytics API"""
    
    segment_id = "697fd30caaa05331f7bb1ad6"  # UK All Users
    
    endpoints_to_try = [
        f"https://api-{DATA_CENTER}.moengage.com/v3/custom-segments/{segment_id}/analytics",
        f"https://api-{DATA_CENTER}.moengage.com/v3/custom-segments/{segment_id}/stats",
        f"https://api-{DATA_CENTER}.moengage.com/v3/custom-segments/{segment_id}/count",
        f"https://api-{DATA_CENTER}.moengage.com/v3/custom-segments/{segment_id}/size",
        f"https://api-{DATA_CENTER}.moengage.com/v1/segments/{segment_id}/count",
        f"https://api-{DATA_CENTER}.moengage.com/v2/segments/{segment_id}/count",
    ]
    
    # Auth
    auth_string = f"{WORKSPACE_ID}:{DATA_API_KEY}"
    encoded_auth = base64.b64encode(auth_string.encode()).decode()
    
    headers = {
        'Authorization': f'Basic {encoded_auth}',
        'Content-Type': 'application/json',
        'MOE-APPKEY': WORKSPACE_ID
    }
    
    print("🔍 Testing various segment count endpoints...")
    
    for url in endpoints_to_try:
        try:
            print(f"\nTrying: {url}")
            response = requests.get(url, headers=headers, timeout=10)
            print(f"Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ SUCCESS! Response: {json.dumps(data, indent=2)}")
                return True
            elif response.status_code == 404:
                print("❌ Not Found")
            elif response.status_code == 403:
                print("❌ Forbidden")
            else:
                print(f"❌ Error: {response.text}")
                
        except Exception as e:
            print(f"❌ Exception: {e}")
    
    return False

def test_dashboard_api():
    """Test if there's a dashboard API that might return segment counts"""
    
    endpoints_to_try = [
        f"https://api-{DATA_CENTER}.moengage.com/v1/dashboard/segments",
        f"https://api-{DATA_CENTER}.moengage.com/v2/dashboard/segments",
        f"https://api-{DATA_CENTER}.moengage.com/v3/dashboard/segments",
        f"https://dashboard-{DATA_CENTER}.moengage.com/api/segments",
    ]
    
    # Try both DATA API and CAMPAIGN API credentials
    auth_configs = [
        ("DATA API", f"{WORKSPACE_ID}:{DATA_API_KEY}"),
        ("CAMPAIGN API", f"{WORKSPACE_ID}:{CAMPAIGN_API_KEY}")
    ]
    
    print("\n🔍 Testing dashboard APIs...")
    
    for auth_name, auth_string in auth_configs:
        encoded_auth = base64.b64encode(auth_string.encode()).decode()
        
        headers = {
            'Authorization': f'Basic {encoded_auth}',
            'Content-Type': 'application/json',
            'MOE-APPKEY': WORKSPACE_ID
        }
        
        if auth_name == "CAMPAIGN API":
            headers['APP_SECRET_KEY'] = CAMPAIGN_API_KEY
        
        print(f"\n--- Using {auth_name} ---")
        
        for url in endpoints_to_try:
            try:
                print(f"Trying: {url}")
                response = requests.get(url, headers=headers, timeout=10)
                print(f"Status: {response.status_code}")
                
                if response.status_code == 200:
                    data = response.json()
                    print(f"✅ SUCCESS! Response: {json.dumps(data, indent=2)[:500]}...")
                    return True
                elif response.status_code == 404:
                    print("❌ Not Found")
                elif response.status_code == 403:
                    print("❌ Forbidden")
                else:
                    print(f"❌ Error: {response.text[:200]}")
                    
            except Exception as e:
                print(f"❌ Exception: {e}")
    
    return False

def test_segment_export_api():
    """Test if there's a segment export API"""
    
    segment_id = "697fd30caaa05331f7bb1ad6"  # UK All Users
    
    endpoints_to_try = [
        f"https://api-{DATA_CENTER}.moengage.com/v3/custom-segments/{segment_id}/export",
        f"https://api-{DATA_CENTER}.moengage.com/v3/custom-segments/{segment_id}/users",
        f"https://api-{DATA_CENTER}.moengage.com/v1/segments/{segment_id}/export",
    ]
    
    # Auth
    auth_string = f"{WORKSPACE_ID}:{DATA_API_KEY}"
    encoded_auth = base64.b64encode(auth_string.encode()).decode()
    
    headers = {
        'Authorization': f'Basic {encoded_auth}',
        'Content-Type': 'application/json',
        'MOE-APPKEY': WORKSPACE_ID
    }
    
    print("\n🔍 Testing segment export endpoints...")
    
    for url in endpoints_to_try:
        try:
            print(f"\nTrying: {url}")
            response = requests.get(url, headers=headers, timeout=10)
            print(f"Status: {response.status_code}")
            
            if response.status_code == 200:
                # Check if it's JSON or file download
                content_type = response.headers.get('content-type', '')
                if 'json' in content_type:
                    data = response.json()
                    print(f"✅ JSON Response: {json.dumps(data, indent=2)[:500]}...")
                else:
                    print(f"✅ File Response: {len(response.content)} bytes, Content-Type: {content_type}")
                return True
            elif response.status_code == 404:
                print("❌ Not Found")
            elif response.status_code == 403:
                print("❌ Forbidden")
            else:
                print(f"❌ Error: {response.text[:200]}")
                
        except Exception as e:
            print(f"❌ Exception: {e}")
    
    return False

def main():
    print("Testing MoEngage APIs for Segment Count Data")
    print("=" * 60)
    
    found_any = False
    
    # Test segment analytics
    if test_segment_analytics_api():
        found_any = True
    
    # Test dashboard APIs
    if test_dashboard_api():
        found_any = True
    
    # Test export APIs
    if test_segment_export_api():
        found_any = True
    
    print("\n" + "=" * 60)
    if found_any:
        print("🎉 Found API that might return segment counts!")
    else:
        print("❌ No APIs found that return segment counts.")
        print("📝 Conclusion: Manual entry from MoEngage dashboard is required.")

if __name__ == "__main__":
    main()