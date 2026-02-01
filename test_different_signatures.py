#!/usr/bin/env python3
"""
Test different signature approaches for MoEngage Report API
"""

import requests
import base64
import hashlib
import hmac
from config import MOENGAGE_APP_ID, CAMPAIGN_API_KEY, DATA_API_KEY, DATA_CENTER

def test_signature_approach(workspace_id, filename, secret_key, algorithm='sha256', message_format=1):
    """Test different signature generation approaches"""
    
    # Different message formats to try
    if message_format == 1:
        message = f"{workspace_id}{filename}{secret_key}"
    elif message_format == 2:
        message = f"{workspace_id}_{filename}_{secret_key}"
    elif message_format == 3:
        message = f"{filename}{workspace_id}{secret_key}"
    elif message_format == 4:
        message = f"{secret_key}{workspace_id}{filename}"
    else:
        message = f"{workspace_id}|{filename}|{secret_key}"
    
    # Different algorithms
    if algorithm == 'md5':
        signature = hashlib.md5(message.encode()).hexdigest()
    elif algorithm == 'sha1':
        signature = hashlib.sha1(message.encode()).hexdigest()
    elif algorithm == 'sha256_direct':
        signature = hashlib.sha256(message.encode()).hexdigest()
    else:  # hmac-sha256
        signature = hmac.new(
            secret_key.encode('utf-8'),
            message.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
    
    return signature, message

def test_report_with_different_approaches():
    """Test report API with different signature approaches"""
    
    filename = "API_Test_PN_report_20260128"
    url = f"https://api-{DATA_CENTER}.moengage.com/campaign_reports/rest_api/{MOENGAGE_APP_ID}/{filename}"
    
    # Basic auth
    auth_string = f"{MOENGAGE_APP_ID}:{CAMPAIGN_API_KEY}"
    encoded_auth = base64.b64encode(auth_string.encode()).decode()
    headers = {
        'Authorization': f'Basic {encoded_auth}',
        'MOE-APPKEY': MOENGAGE_APP_ID
    }
    
    # Test different combinations
    test_cases = [
        # (secret_key, algorithm, message_format, description)
        (CAMPAIGN_API_KEY, 'hmac-sha256', 1, 'Campaign API Key + HMAC-SHA256 + Format1'),
        (DATA_API_KEY, 'hmac-sha256', 1, 'Data API Key + HMAC-SHA256 + Format1'),
        (CAMPAIGN_API_KEY, 'sha256_direct', 1, 'Campaign API Key + SHA256 Direct + Format1'),
        (CAMPAIGN_API_KEY, 'md5', 1, 'Campaign API Key + MD5 + Format1'),
        (CAMPAIGN_API_KEY, 'hmac-sha256', 2, 'Campaign API Key + HMAC-SHA256 + Format2 (underscores)'),
        (CAMPAIGN_API_KEY, 'hmac-sha256', 3, 'Campaign API Key + HMAC-SHA256 + Format3 (filename first)'),
        ('', 'sha256_direct', 1, 'Empty secret + SHA256 Direct'),
        (MOENGAGE_APP_ID, 'hmac-sha256', 1, 'Workspace ID as secret + HMAC-SHA256'),
    ]
    
    print(f"Testing Report API with Different Signature Approaches")
    print(f"URL: {url}")
    print("=" * 80)
    
    for secret_key, algorithm, msg_format, description in test_cases:
        print(f"\n{description}")
        print("-" * 50)
        
        signature, message = test_signature_approach(MOENGAGE_APP_ID, filename, secret_key, algorithm, msg_format)
        
        print(f"Secret: {secret_key}")
        print(f"Message: {message}")
        print(f"Signature: {signature}")
        
        params = {'signature': signature}
        
        try:
            response = requests.get(url, headers=headers, params=params, timeout=15)
            print(f"Status: {response.status_code}")
            
            if response.status_code == 200:
                print("✅ SUCCESS!")
                print(f"Content length: {len(response.text)}")
                lines = response.text.split('\n')[:3]
                print("First 3 lines:")
                for line in lines:
                    print(f"  {line}")
                return response.text
                
            elif response.status_code == 400:
                error_msg = response.text
                if "SIGNATURE" in error_msg:
                    print("❌ Signature still invalid")
                else:
                    print(f"❌ Different error: {error_msg[:100]}")
            else:
                print(f"❌ Status {response.status_code}: {response.text[:100]}")
                
        except requests.exceptions.RequestException as e:
            print(f"💥 Error: {e}")
    
    return None

def main():
    print("MoEngage Report API - Comprehensive Signature Test")
    print("=" * 60)
    
    result = test_report_with_different_approaches()
    
    if result:
        print(f"\n🎉 SUCCESS! Found working signature method.")
    else:
        print(f"\n❌ No signature method worked.")
        print("Possible solutions:")
        print("1. Contact MoEngage support for the correct SECRET-KEY")
        print("2. Check if report needs to be 'generated' first")
        print("3. Verify report configuration in dashboard")

if __name__ == "__main__":
    main()