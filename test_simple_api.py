#!/usr/bin/env python3
"""
Test simple MoEngage API endpoints to verify connection
"""

import requests
import base64
from config import MOENGAGE_APP_ID, MOENGAGE_API_KEY, DATA_CENTER

def test_simple_endpoint():
    """Test a simple endpoint to verify basic connectivity"""
    
    # Create auth header
    auth_string = f"{MOENGAGE_APP_ID}:{MOENGAGE_API_KEY}"
    encoded_auth = base64.b64encode(auth_string.encode()).decode()
    
    headers = {
        'Authorization': f'Basic {encoded_auth}',
        'Content-Type': 'application/json',
        'MOE-APPKEY': MOENGAGE_APP_ID
    }
    
    # Try different possible endpoints
    endpoints_to_test = [
        f"https://api-{DATA_CENTER}.moengage.com/v1/campaigns/stats",
        f"https://api-{DATA_CENTER}.moengage.com/v1/stats",
        f"https://api-{DATA_CENTER}.moengage.com/v1/segments",
        f"https://api-{DATA_CENTER}.moengage.com/v1/transition/{MOENGAGE_APP_ID}",
        f"https://api-{DATA_CENTER}.moengage.com/v1/campaigns",
    ]
    
    for endpoint in endpoints_to_test:
        print(f"\nTesting: {endpoint}")
        
        try:
            # Try GET first
            response = requests.get(endpoint, headers=headers, timeout=10)
            print(f"GET Status: {response.status_code}")
            if response.status_code != 404:
                print(f"GET Response: {response.text[:200]}...")
            
            # Try POST if GET doesn't work
            if response.status_code == 404 or response.status_code == 405:
                post_response = requests.post(endpoint, headers=headers, json={}, timeout=10)
                print(f"POST Status: {post_response.status_code}")
                if post_response.status_code != 404:
                    print(f"POST Response: {post_response.text[:200]}...")
                    
        except requests.exceptions.RequestException as e:
            print(f"Error: {e}")

def main():
    print("Testing MoEngage API Endpoints")
    print("=" * 40)
    print(f"Workspace ID: {MOENGAGE_APP_ID}")
    print(f"Data Center: {DATA_CENTER}")
    
    test_simple_endpoint()

if __name__ == "__main__":
    main()