#!/usr/bin/env python3
"""
Test the simple report API endpoint provided by MoEngage team
"""

import requests
import base64
from config import MOENGAGE_APP_ID, CAMPAIGN_API_KEY, DATA_CENTER

def test_simple_report_api():
    """Test the simple GET endpoint for reports"""
    
    # The URL structure provided by MoEngage team
    url = f"https://api-{DATA_CENTER}.moengage.com/campaign_reports/rest_api/{MOENGAGE_APP_ID}/API_Test_PN_report_20260128"
    
    # Try different authentication approaches
    auth_approaches = [
        # 1. Basic auth with campaign API key
        {
            'headers': {
                'Authorization': f'Basic {base64.b64encode(f"{MOENGAGE_APP_ID}:{CAMPAIGN_API_KEY}".encode()).decode()}',
                'MOE-APPKEY': MOENGAGE_APP_ID
            },
            'description': 'Basic auth with Campaign API key'
        },
        # 2. Just basic auth
        {
            'headers': {
                'Authorization': f'Basic {base64.b64encode(f"{MOENGAGE_APP_ID}:{CAMPAIGN_API_KEY}".encode()).decode()}'
            },
            'description': 'Basic auth only'
        },
        # 3. No auth (maybe it's public)
        {
            'headers': {},
            'description': 'No authentication'
        }
    ]
    
    print(f"Testing Simple Report API")
    print(f"URL: {url}")
    print("=" * 60)
    
    for i, approach in enumerate(auth_approaches, 1):
        print(f"\n{i}. {approach['description']}")
        print("-" * 30)
        
        try:
            response = requests.get(url, headers=approach['headers'], timeout=30)
            print(f"Status Code: {response.status_code}")
            
            if response.status_code == 200:
                print("✅ SUCCESS!")
                content_type = response.headers.get('content-type', 'unknown')
                print(f"Content Type: {content_type}")
                print(f"Content Length: {len(response.text)} characters")
                
                # Show first few lines if it's CSV
                if 'csv' in content_type.lower() or response.text.startswith('"') or ',' in response.text[:100]:
                    lines = response.text.split('\n')[:5]
                    print("First 5 lines:")
                    for line in lines:
                        print(f"  {line}")
                else:
                    print(f"First 200 chars: {response.text[:200]}")
                
                return response.text
                
            elif response.status_code == 401:
                print("❌ Authentication required")
                
            elif response.status_code == 404:
                print("❌ Report not found")
                
            elif response.status_code == 403:
                print("❌ Access forbidden")
                
            else:
                print(f"❌ Error {response.status_code}")
                print(f"Response: {response.text[:200]}")
                
        except requests.exceptions.RequestException as e:
            print(f"💥 Connection error: {e}")
    
    return None

def main():
    print("MoEngage Simple Report API Test")
    print("=" * 40)
    print(f"Workspace ID: {MOENGAGE_APP_ID}")
    print(f"Data Center: {DATA_CENTER}")
    print()
    
    result = test_simple_report_api()
    
    if result:
        print("\n🎉 SUCCESS! The report API is working.")
        print("We can now build the full automation.")
    else:
        print("\n❌ Report API not working yet.")
        print("May need to wait for report generation or check authentication.")

if __name__ == "__main__":
    main()