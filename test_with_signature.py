#!/usr/bin/env python3
"""
Test report API with signature using different secret keys
"""

import requests
import base64
import hashlib
import hmac
from config import MOENGAGE_APP_ID, CAMPAIGN_API_KEY, DATA_API_KEY, DATA_CENTER

def generate_signature(workspace_id, filename, secret_key):
    """Generate signature for report API"""
    message = f"{workspace_id}{filename}{secret_key}"
    signature = hmac.new(
        secret_key.encode('utf-8'),
        message.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()
    return signature

def test_with_signature(secret_key, description):
    """Test report API with signature"""
    
    filename = "API_Test_PN_report_20260128"
    signature = generate_signature(MOENGAGE_APP_ID, filename, secret_key)
    
    url = f"https://api-{DATA_CENTER}.moengage.com/campaign_reports/rest_api/{MOENGAGE_APP_ID}/{filename}"
    
    # Try with signature as query parameter
    params = {'signature': signature}
    
    # Basic auth
    auth_string = f"{MOENGAGE_APP_ID}:{CAMPAIGN_API_KEY}"
    encoded_auth = base64.b64encode(auth_string.encode()).decode()
    
    headers = {
        'Authorization': f'Basic {encoded_auth}',
        'MOE-APPKEY': MOENGAGE_APP_ID
    }
    
    print(f"\n{description}")
    print(f"Secret key: {secret_key}")
    print(f"Signature: {signature}")
    print("-" * 50)
    
    try:
        response = requests.get(url, headers=headers, params=params, timeout=30)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ SUCCESS!")
            print(f"Content Length: {len(response.text)} characters")
            
            # Show first few lines
            lines = response.text.split('\n')[:3]
            print("First 3 lines:")
            for line in lines:
                print(f"  {line}")
            
            return response.text
            
        else:
            print(f"❌ Error: {response.text[:200]}")
            
    except requests.exceptions.RequestException as e:
        print(f"💥 Error: {e}")
    
    return None

def main():
    print("MoEngage Report API - Signature Test")
    print("=" * 40)
    
    # Try different possible secret keys
    test_cases = [
        (CAMPAIGN_API_KEY, "Using Campaign API Key as secret"),
        (DATA_API_KEY, "Using Data API Key as secret"),
        (MOENGAGE_APP_ID, "Using Workspace ID as secret"),
        ("moengage", "Using 'moengage' as secret"),
        ("", "Using empty string as secret"),
    ]
    
    for secret_key, description in test_cases:
        result = test_with_signature(secret_key, description)
        if result:
            print(f"\n🎉 SUCCESS! Found working secret key: {secret_key}")
            break
    else:
        print(f"\n❌ None of the secret keys worked.")
        print("Need to get the correct secret key from MoEngage team.")

if __name__ == "__main__":
    main()