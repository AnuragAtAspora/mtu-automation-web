#!/usr/bin/env python3
"""
Test MoEngage Report API with the correct signature format from chatbot
"""

import requests
import base64
import hashlib
from config import MOENGAGE_APP_ID, CAMPAIGN_API_KEY, DATA_API_KEY, DATA_CENTER

def generate_signature_correct_format(app_id, filename, secret_key):
    """Generate signature using the correct format from MoEngage chatbot"""
    # Format: App_ID + "|" + FILENAME + "|" + SECRET_KEY
    signature_key = f"{app_id}|{filename}|{secret_key}"
    
    # Use SHA-256 direct hash (not HMAC)
    signature = hashlib.sha256(signature_key.encode('utf-8')).hexdigest()
    
    return signature, signature_key

def test_with_correct_format():
    """Test report API with correct signature format"""
    
    filename = "API_Test_PN_report_20260128"
    
    # Try different possible secret keys
    secret_keys_to_try = [
        (CAMPAIGN_API_KEY, "Campaign API Key"),
        (DATA_API_KEY, "Data API Key"),
        (MOENGAGE_APP_ID, "Workspace ID"),
        ("", "Empty string"),
        ("moengage", "Default 'moengage'"),
    ]
    
    url = f"https://api-{DATA_CENTER}.moengage.com/campaign_reports/rest_api/{MOENGAGE_APP_ID}/{filename}"
    
    # Basic auth
    auth_string = f"{MOENGAGE_APP_ID}:{CAMPAIGN_API_KEY}"
    encoded_auth = base64.b64encode(auth_string.encode()).decode()
    
    print("Testing MoEngage Report API - Correct Signature Format")
    print("=" * 60)
    print(f"URL: {url}")
    print(f"Format: App_ID|FILENAME|SECRET_KEY")
    print()
    
    for secret_key, description in secret_keys_to_try:
        print(f"Testing with {description}: {secret_key}")
        print("-" * 50)
        
        # Generate signature
        signature, signature_key = generate_signature_correct_format(MOENGAGE_APP_ID, filename, secret_key)
        
        print(f"Signature Key: {signature_key}")
        print(f"SHA-256 Hash: {signature}")
        
        # Headers with signature (as per chatbot instruction)
        headers = {
            'Authorization': f'Basic {encoded_auth}',
            'MOE-APPKEY': MOENGAGE_APP_ID,
            'Signature': signature  # Signature in header, not query param
        }
        
        try:
            response = requests.get(url, headers=headers, timeout=30)
            print(f"Status Code: {response.status_code}")
            
            if response.status_code == 200:
                print("✅ SUCCESS!")
                print(f"Content Length: {len(response.text)} characters")
                
                # Show first few lines
                lines = response.text.split('\n')[:5]
                print("First 5 lines:")
                for line in lines:
                    print(f"  {line}")
                
                # Save to file
                with open('downloaded_report.csv', 'w') as f:
                    f.write(response.text)
                print("📁 Report saved as 'downloaded_report.csv'")
                
                return response.text
                
            elif response.status_code == 400:
                error_text = response.text
                print(f"❌ Bad Request: {error_text}")
                
                # Check if it's still signature error
                if "SIGNATURE" in error_text:
                    print("   Still signature issue")
                else:
                    print("   ⚠️  Different error - progress!")
                    
            else:
                print(f"❌ Status {response.status_code}: {response.text[:200]}")
                
        except requests.exceptions.RequestException as e:
            print(f"💥 Connection error: {e}")
        
        print()
    
    return None

def main():
    result = test_with_correct_format()
    
    if result:
        print("🎉 SUCCESS! Found the working secret key and format.")
        print("We can now build the full automation.")
    else:
        print("❌ Still need the correct SECRET_KEY.")
        print("Ask MoEngage support: 'What is the SECRET_KEY for report API signatures?'")
        print("It should be different from the Campaign API Key.")

if __name__ == "__main__":
    main()