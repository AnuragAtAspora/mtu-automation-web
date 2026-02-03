#!/usr/bin/env python3
"""
Implement MoEngage Stats API based on documentation patterns
"""

import requests
import base64
import json
import hashlib
from datetime import datetime, timedelta

# Configuration
MOENGAGE_CONFIG = {
    'workspace_id': '95PNUHBSYSLLJZ22PEOFMKF2',
    'data_api_key': 'Mj5JSGKcwYum9NKAGmGHJG_E',
    'campaign_api_key': '3XMHJ83D2X4V',
    'data_center': '01'
}

def test_stats_api_with_proper_auth():
    """Test Stats API with different authentication methods"""
    
    # Based on the 401 error mentioning APP_SECRET_KEY, let's try different auth approaches
    
    # Method 1: Try with signature-based auth (like Campaign Report API)
    print("🧪 Method 1: Signature-based authentication")
    
    url = f"https://api-{MOENGAGE_CONFIG['data_center']}.moengage.com/v1/campaigns/stats"
    
    # Generate signature similar to Campaign Report API
    signature_key = f"{MOENGAGE_CONFIG['workspace_id']}|stats|{MOENGAGE_CONFIG['campaign_api_key']}"
    signature = hashlib.sha256(signature_key.encode('utf-8')).hexdigest()
    
    auth_string = f"{MOENGAGE_CONFIG['workspace_id']}:{MOENGAGE_CONFIG['campaign_api_key']}"
    encoded_auth = base64.b64encode(auth_string.encode()).decode()
    
    headers = {
        'Authorization': f'Basic {encoded_auth}',
        'MOE-APPKEY': MOENGAGE_CONFIG['workspace_id'],
        'Signature': signature,
        'Content-Type': 'application/json'
    }
    
    payload = {
        'start_date': '2026-01-01',
        'end_date': '2026-01-31',
        'campaign_types': ['push', 'email'],
        'metrics': ['sent', 'delivered', 'opened', 'clicked']
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            print("✅ Method 1 Success!")
            return response.json()
        else:
            print(f"❌ Method 1 Failed: {response.text}")
    except Exception as e:
        print(f"❌ Method 1 Exception: {str(e)}")
    
    # Method 2: Try with APP_SECRET_KEY header
    print("\n🧪 Method 2: APP_SECRET_KEY header")
    
    headers = {
        'Authorization': f'Basic {encoded_auth}',
        'MOE-APPKEY': MOENGAGE_CONFIG['workspace_id'],
        'APP_SECRET_KEY': MOENGAGE_CONFIG['campaign_api_key'],
        'Content-Type': 'application/json'
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            print("✅ Method 2 Success!")
            return response.json()
        else:
            print(f"❌ Method 2 Failed: {response.text}")
    except Exception as e:
        print(f"❌ Method 2 Exception: {str(e)}")
    
    # Method 3: Try different endpoint structure
    print("\n🧪 Method 3: Different endpoint structure")
    
    url = f"https://api-{MOENGAGE_CONFIG['data_center']}.moengage.com/core-services/v1/campaigns/stats"
    
    headers = {
        'Authorization': f'Basic {encoded_auth}',
        'MOE-APPKEY': MOENGAGE_CONFIG['workspace_id'],
        'Content-Type': 'application/json'
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            print("✅ Method 3 Success!")
            return response.json()
        else:
            print(f"❌ Method 3 Failed: {response.text}")
    except Exception as e:
        print(f"❌ Method 3 Exception: {str(e)}")
    
    # Method 4: Try GET request with query parameters
    print("\n🧪 Method 4: GET request with query parameters")
    
    url = f"https://api-{MOENGAGE_CONFIG['data_center']}.moengage.com/v1/campaigns/stats"
    
    params = {
        'start_date': '2026-01-01',
        'end_date': '2026-01-31',
        'campaign_types': 'push,email',
        'metrics': 'sent,delivered,opened'
    }
    
    try:
        response = requests.get(url, params=params, headers=headers, timeout=30)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            print("✅ Method 4 Success!")
            return response.json()
        else:
            print(f"❌ Method 4 Failed: {response.text}")
    except Exception as e:
        print(f"❌ Method 4 Exception: {str(e)}")
    
    return None

def test_campaign_search_with_stats():
    """Test the campaign search API that we know exists but with stats included"""
    
    print("\n🧪 Testing Campaign Search API with stats")
    
    url = f"https://api-{MOENGAGE_CONFIG['data_center']}.moengage.com/core-services/v1/campaigns/search"
    
    # Try with Data API credentials
    auth_string = f"{MOENGAGE_CONFIG['workspace_id']}:{MOENGAGE_CONFIG['data_api_key']}"
    encoded_auth = base64.b64encode(auth_string.encode()).decode()
    
    headers = {
        'Authorization': f'Basic {encoded_auth}',
        'MOE-APPKEY': MOENGAGE_CONFIG['workspace_id'],
        'Content-Type': 'application/json'
    }
    
    # Payload to search for campaigns with stats
    payload = {
        "filters": {
            "campaign_type": ["push", "email"],
            "status": ["sent", "completed"],
            "sent_date": {
                "start_date": "2026-01-01T00:00:00.000Z",
                "end_date": "2026-01-31T23:59:59.999Z"
            }
        },
        "include_stats": True,
        "include_performance": True,
        "page_size": 1000,
        "sort_by": "sent_date",
        "sort_order": "desc"
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Campaign Search Success!")
            
            if isinstance(data, dict) and 'campaigns' in data:
                campaigns = data['campaigns']
                print(f"Found {len(campaigns)} campaigns")
                
                # Aggregate stats by country and type
                stats = {
                    'uk_push_sent': 0,
                    'uk_email_sent': 0,
                    'uae_push_sent': 0,
                    'uae_email_sent': 0
                }
                
                for campaign in campaigns:
                    name = campaign.get('name', '').lower()
                    campaign_type = campaign.get('campaign_type', '').lower()
                    
                    # Look for stats in different possible locations
                    sent_count = 0
                    if 'stats' in campaign:
                        sent_count = campaign['stats'].get('sent', 0)
                    elif 'performance' in campaign:
                        sent_count = campaign['performance'].get('sent', 0)
                    elif 'metrics' in campaign:
                        sent_count = campaign['metrics'].get('sent', 0)
                    
                    # Aggregate by country and type
                    if 'uk' in name:
                        if 'push' in campaign_type:
                            stats['uk_push_sent'] += sent_count
                        elif 'email' in campaign_type:
                            stats['uk_email_sent'] += sent_count
                    elif 'uae' in name:
                        if 'push' in campaign_type:
                            stats['uae_push_sent'] += sent_count
                        elif 'email' in campaign_type:
                            stats['uae_email_sent'] += sent_count
                
                print(f"📊 Aggregated Stats:")
                for key, value in stats.items():
                    print(f"  {key}: {value:,}")
                
                return stats
            else:
                print(f"Response structure: {list(data.keys()) if isinstance(data, dict) else 'Not a dict'}")
                
        else:
            print(f"❌ Failed: {response.text}")
            
    except Exception as e:
        print(f"❌ Exception: {str(e)}")
    
    return None

def main():
    print("🔍 IMPLEMENTING MOENGAGE STATS API")
    print("=" * 50)
    
    # Test different approaches
    result1 = test_stats_api_with_proper_auth()
    result2 = test_campaign_search_with_stats()
    
    print("\n" + "=" * 50)
    print("📊 RESULTS:")
    
    if result1:
        print("✅ Stats API working!")
    elif result2:
        print("✅ Campaign Search API with stats working!")
        print("This can be used as alternative to Stats API")
    else:
        print("❌ No working API found")
        print("Possible next steps:")
        print("1. Contact MoEngage support to enable Stats API")
        print("2. Check if your account has access to these APIs")
        print("3. Verify correct authentication method")

if __name__ == "__main__":
    main()