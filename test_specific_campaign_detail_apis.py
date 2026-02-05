#!/usr/bin/env python3
"""
Test the specific Get Email Campaign Details API and Get Push Campaign Details API
Based on the official documentation links provided by the user
"""

import requests
import base64
import json
from datetime import datetime, timedelta

# Configuration
MOENGAGE_CONFIG = {
    'workspace_id': '95PNUHBSYSLLJZ22PEOFMKF2',
    'data_api_key': 'Mj5JSGKcwYum9NKAGmGHJG_E',
    'campaign_api_key': '3XMHJ83D2X4V',
    'data_center': '01'
}

def test_email_campaign_details_api():
    """Test the specific Get Email Campaign Details API"""
    
    print("🔍 TESTING GET EMAIL CAMPAIGN DETAILS API")
    print("=" * 60)
    print("📚 Documentation: https://developers.moengage.com/hc/en-us/articles/27896777540756-Get-Email-Campaign-Details")
    
    # Based on the pattern from other MoEngage APIs, try different possible endpoints
    possible_endpoints = [
        "/core-services/v1/campaigns/search",  # Current endpoint I'm using
        "/core-services/v1/email-campaigns/search",  # Email-specific endpoint
        "/core-services/v1/email/campaigns/search",  # Alternative email endpoint
        "/core-services/v1/campaigns/email/search",  # Alternative structure
        "/v1/email-campaigns/search",  # V1 email endpoint
        "/v1/campaigns/email/search",  # V1 alternative
        "/email/v1/campaigns/search",  # Email service endpoint
        "/campaigns/v1/email/search"   # Campaigns service endpoint
    ]
    
    auth_string = f"{MOENGAGE_CONFIG['workspace_id']}:{MOENGAGE_CONFIG['campaign_api_key']}"
    encoded_auth = base64.b64encode(auth_string.encode()).decode()
    
    headers = {
        'Authorization': f'Basic {encoded_auth}',
        'MOE-APPKEY': MOENGAGE_CONFIG['workspace_id'],
        'APP_SECRET_KEY': MOENGAGE_CONFIG['campaign_api_key'],
        'Content-Type': 'application/json'
    }
    
    # Test payload for email campaigns
    payload = {
        "request_id": f"email_api_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
        "limit": 5,
        "page": 1,
        "campaign_fields": {
            "channels": ["EMAIL"],  # Email campaigns only
            "created_date": {
                "from_date": "2026-02-01",
                "to_date": "2026-02-28"
            }
        }
    }
    
    working_endpoints = []
    
    for endpoint in possible_endpoints:
        url = f"https://api-{MOENGAGE_CONFIG['data_center']}.moengage.com{endpoint}"
        
        try:
            print(f"\nTesting: {endpoint}")
            response = requests.post(url, json=payload, headers=headers, timeout=20)
            
            if response.status_code == 200:
                campaigns = response.json()
                email_campaigns = [c for c in campaigns if c.get('channel', '').upper() == 'EMAIL']
                
                print(f"✅ SUCCESS: {len(campaigns)} total, {len(email_campaigns)} email campaigns")
                
                if email_campaigns:
                    sample = email_campaigns[0]
                    basic_details = sample.get('basic_details', {})
                    print(f"  Sample: {basic_details.get('name', 'Unknown')} | {sample.get('status', 'Unknown')}")
                    
                    # Check for performance data
                    performance_keys = []
                    for key in sample.keys():
                        if any(word in key.lower() for word in ['stat', 'metric', 'performance', 'sent', 'delivered', 'open', 'click']):
                            performance_keys.append(key)
                    
                    if performance_keys:
                        print(f"  📊 Performance keys: {performance_keys}")
                        for key in performance_keys:
                            print(f"    {key}: {sample[key]}")
                    else:
                        print(f"  📋 Available keys: {list(sample.keys())}")
                
                working_endpoints.append({
                    'endpoint': endpoint,
                    'campaigns': campaigns,
                    'email_campaigns': email_campaigns
                })
                
            elif response.status_code == 404:
                print(f"❌ 404 - Not found")
            elif response.status_code == 403:
                print(f"🔒 403 - Forbidden")
            elif response.status_code == 400:
                error_data = response.json() if response.headers.get('content-type', '').startswith('application/json') else response.text
                print(f"❌ 400 - Bad Request: {error_data}")
            else:
                print(f"❓ {response.status_code}")
                
        except Exception as e:
            print(f"❌ Exception: {str(e)}")
    
    return working_endpoints

def test_push_campaign_details_api():
    """Test the specific Get Push Campaign Details API"""
    
    print("\n🔍 TESTING GET PUSH CAMPAIGN DETAILS API")
    print("=" * 60)
    print("📚 Documentation: https://developers.moengage.com/hc/en-us/articles/38466670624276-Get-Push-Campaign-Details")
    
    # Try different possible endpoints for Push campaigns
    possible_endpoints = [
        "/core-services/v1/campaigns/search",  # Current endpoint I'm using
        "/core-services/v1/push-campaigns/search",  # Push-specific endpoint
        "/core-services/v1/push/campaigns/search",  # Alternative push endpoint
        "/core-services/v1/campaigns/push/search",  # Alternative structure
        "/v1/push-campaigns/search",  # V1 push endpoint
        "/v1/campaigns/push/search",  # V1 alternative
        "/push/v1/campaigns/search",  # Push service endpoint
        "/campaigns/v1/push/search"   # Campaigns service endpoint
    ]
    
    auth_string = f"{MOENGAGE_CONFIG['workspace_id']}:{MOENGAGE_CONFIG['campaign_api_key']}"
    encoded_auth = base64.b64encode(auth_string.encode()).decode()
    
    headers = {
        'Authorization': f'Basic {encoded_auth}',
        'MOE-APPKEY': MOENGAGE_CONFIG['workspace_id'],
        'APP_SECRET_KEY': MOENGAGE_CONFIG['campaign_api_key'],
        'Content-Type': 'application/json'
    }
    
    # Test payload for push campaigns
    payload = {
        "request_id": f"push_api_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
        "limit": 5,
        "page": 1,
        "campaign_fields": {
            "channels": ["PUSH"],  # Push campaigns only
            "created_date": {
                "from_date": "2026-02-01",
                "to_date": "2026-02-28"
            }
        }
    }
    
    working_endpoints = []
    
    for endpoint in possible_endpoints:
        url = f"https://api-{MOENGAGE_CONFIG['data_center']}.moengage.com{endpoint}"
        
        try:
            print(f"\nTesting: {endpoint}")
            response = requests.post(url, json=payload, headers=headers, timeout=20)
            
            if response.status_code == 200:
                campaigns = response.json()
                push_campaigns = [c for c in campaigns if c.get('channel', '').upper() == 'PUSH']
                
                print(f"✅ SUCCESS: {len(campaigns)} total, {len(push_campaigns)} push campaigns")
                
                if push_campaigns:
                    sample = push_campaigns[0]
                    basic_details = sample.get('basic_details', {})
                    print(f"  Sample: {basic_details.get('name', 'Unknown')} | {sample.get('status', 'Unknown')}")
                    
                    # Check for performance data
                    performance_keys = []
                    for key in sample.keys():
                        if any(word in key.lower() for word in ['stat', 'metric', 'performance', 'sent', 'delivered', 'open', 'click']):
                            performance_keys.append(key)
                    
                    if performance_keys:
                        print(f"  📊 Performance keys: {performance_keys}")
                        for key in performance_keys:
                            print(f"    {key}: {sample[key]}")
                    else:
                        print(f"  📋 Available keys: {list(sample.keys())}")
                
                working_endpoints.append({
                    'endpoint': endpoint,
                    'campaigns': campaigns,
                    'push_campaigns': push_campaigns
                })
                
            elif response.status_code == 404:
                print(f"❌ 404 - Not found")
            elif response.status_code == 403:
                print(f"🔒 403 - Forbidden")
            elif response.status_code == 400:
                error_data = response.json() if response.headers.get('content-type', '').startswith('application/json') else response.text
                print(f"❌ 400 - Bad Request: {error_data}")
            else:
                print(f"❓ {response.status_code}")
                
        except Exception as e:
            print(f"❌ Exception: {str(e)}")
    
    return working_endpoints

def test_alternative_authentication_methods():
    """Test if different authentication methods work for these APIs"""
    
    print("\n🔍 TESTING ALTERNATIVE AUTHENTICATION METHODS")
    print("=" * 60)
    
    # Test with Data API credentials instead of Campaign API
    auth_methods = [
        {
            'name': 'Campaign API (current)',
            'auth_string': f"{MOENGAGE_CONFIG['workspace_id']}:{MOENGAGE_CONFIG['campaign_api_key']}",
            'headers': {
                'MOE-APPKEY': MOENGAGE_CONFIG['workspace_id'],
                'APP_SECRET_KEY': MOENGAGE_CONFIG['campaign_api_key']
            }
        },
        {
            'name': 'Data API',
            'auth_string': f"{MOENGAGE_CONFIG['workspace_id']}:{MOENGAGE_CONFIG['data_api_key']}",
            'headers': {
                'MOE-APPKEY': MOENGAGE_CONFIG['workspace_id']
            }
        },
        {
            'name': 'Campaign API without APP_SECRET_KEY',
            'auth_string': f"{MOENGAGE_CONFIG['workspace_id']}:{MOENGAGE_CONFIG['campaign_api_key']}",
            'headers': {
                'MOE-APPKEY': MOENGAGE_CONFIG['workspace_id']
            }
        }
    ]
    
    endpoint = "/core-services/v1/campaigns/search"
    url = f"https://api-{MOENGAGE_CONFIG['data_center']}.moengage.com{endpoint}"
    
    payload = {
        "request_id": f"auth_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
        "limit": 3,
        "page": 1,
        "campaign_fields": {
            "channels": ["EMAIL", "PUSH"]
        }
    }
    
    working_auth_methods = []
    
    for auth_method in auth_methods:
        print(f"\n--- Testing {auth_method['name']} ---")
        
        encoded_auth = base64.b64encode(auth_method['auth_string'].encode()).decode()
        headers = {
            'Authorization': f'Basic {encoded_auth}',
            'Content-Type': 'application/json'
        }
        headers.update(auth_method['headers'])
        
        try:
            response = requests.post(url, json=payload, headers=headers, timeout=20)
            
            if response.status_code == 200:
                campaigns = response.json()
                print(f"✅ SUCCESS: {len(campaigns)} campaigns")
                working_auth_methods.append(auth_method['name'])
            elif response.status_code == 401:
                print(f"🔑 401 - Unauthorized")
            elif response.status_code == 403:
                print(f"🔒 403 - Forbidden")
            else:
                print(f"❓ {response.status_code}")
                
        except Exception as e:
            print(f"❌ Exception: {str(e)}")
    
    return working_auth_methods

def compare_with_current_approach():
    """Compare results with my current approach"""
    
    print("\n🔍 COMPARING WITH CURRENT APPROACH")
    print("=" * 60)
    
    # My current approach
    url = f"https://api-{MOENGAGE_CONFIG['data_center']}.moengage.com/core-services/v1/campaigns/search"
    
    auth_string = f"{MOENGAGE_CONFIG['workspace_id']}:{MOENGAGE_CONFIG['campaign_api_key']}"
    encoded_auth = base64.b64encode(auth_string.encode()).decode()
    
    headers = {
        'Authorization': f'Basic {encoded_auth}',
        'MOE-APPKEY': MOENGAGE_CONFIG['workspace_id'],
        'APP_SECRET_KEY': MOENGAGE_CONFIG['campaign_api_key'],
        'Content-Type': 'application/json'
    }
    
    payload = {
        "request_id": f"current_approach_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
        "limit": 10,
        "page": 1,
        "campaign_fields": {
            "channels": ["EMAIL", "PUSH"],
            "created_date": {
                "from_date": "2026-02-01",
                "to_date": "2026-02-28"
            }
        }
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        
        if response.status_code == 200:
            campaigns = response.json()
            email_campaigns = [c for c in campaigns if c.get('channel', '').upper() == 'EMAIL']
            push_campaigns = [c for c in campaigns if c.get('channel', '').upper() == 'PUSH']
            
            print(f"✅ Current approach works:")
            print(f"  Total campaigns: {len(campaigns)}")
            print(f"  Email campaigns: {len(email_campaigns)}")
            print(f"  Push campaigns: {len(push_campaigns)}")
            
            # Show sample data structure
            if campaigns:
                sample = campaigns[0]
                print(f"\n📊 Sample campaign structure:")
                print(f"  Available keys: {list(sample.keys())}")
                
                basic_details = sample.get('basic_details', {})
                if basic_details:
                    print(f"  Campaign name: {basic_details.get('name', 'Unknown')}")
                    print(f"  Channel: {sample.get('channel', 'Unknown')}")
                    print(f"  Status: {sample.get('status', 'Unknown')}")
            
            return campaigns
        else:
            print(f"❌ Current approach failed: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"❌ Exception: {str(e)}")
        return None

def main():
    """Main function to test specific Email and Push Campaign Details APIs"""
    
    print("🚀 TESTING SPECIFIC EMAIL AND PUSH CAMPAIGN DETAILS APIS")
    print("=" * 80)
    print("📚 Based on official MoEngage documentation:")
    print("  • Get Email Campaign Details: https://developers.moengage.com/hc/en-us/articles/27896777540756-Get-Email-Campaign-Details")
    print("  • Get Push Campaign Details: https://developers.moengage.com/hc/en-us/articles/38466670624276-Get-Push-Campaign-Details")
    print("=" * 80)
    
    # Test Email Campaign Details API
    email_endpoints = test_email_campaign_details_api()
    
    # Test Push Campaign Details API
    push_endpoints = test_push_campaign_details_api()
    
    # Test alternative authentication methods
    working_auth = test_alternative_authentication_methods()
    
    # Compare with current approach
    current_result = compare_with_current_approach()
    
    print(f"\n" + "="*80)
    print("📊 FINAL ANALYSIS")
    print("="*80)
    
    print(f"🔍 EMAIL CAMPAIGN DETAILS API:")
    if email_endpoints:
        print(f"  ✅ {len(email_endpoints)} working endpoints found")
        for endpoint_info in email_endpoints:
            print(f"    • {endpoint_info['endpoint']}: {len(endpoint_info['email_campaigns'])} email campaigns")
    else:
        print(f"  ❌ No specific email endpoints found")
    
    print(f"\n🔍 PUSH CAMPAIGN DETAILS API:")
    if push_endpoints:
        print(f"  ✅ {len(push_endpoints)} working endpoints found")
        for endpoint_info in push_endpoints:
            print(f"    • {endpoint_info['endpoint']}: {len(endpoint_info['push_campaigns'])} push campaigns")
    else:
        print(f"  ❌ No specific push endpoints found")
    
    print(f"\n🔑 AUTHENTICATION METHODS:")
    if working_auth:
        print(f"  ✅ Working methods: {', '.join(working_auth)}")
    else:
        print(f"  ❌ No alternative authentication methods work")
    
    print(f"\n🎯 CONCLUSION:")
    if email_endpoints or push_endpoints:
        print("✅ FOUND SPECIFIC EMAIL/PUSH CAMPAIGN APIS!")
        print("  • These may be the official APIs mentioned in your documentation links")
        print("  • They might have different data structures or performance metrics")
        print("  • Should implement these instead of the generic campaigns/search endpoint")
    elif current_result:
        print("🔄 CURRENT APPROACH IS LIKELY CORRECT:")
        print("  • The /core-services/v1/campaigns/search endpoint works for both Email and Push")
        print("  • It's probably the unified API that handles all campaign types")
        print("  • The documentation links likely point to the same endpoint with different examples")
        print("  • Channel filtering ('EMAIL', 'PUSH') determines the campaign type")
    else:
        print("❌ UNABLE TO CONFIRM API ENDPOINTS")
        print("  • Need to contact MoEngage support for clarification")
        print("  • Documentation may be outdated or access-restricted")

if __name__ == "__main__":
    main()