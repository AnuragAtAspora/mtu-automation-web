#!/usr/bin/env python3
"""
Debug script to test segment creation and see what's happening
"""

import requests
import base64
import json
from datetime import datetime, timedelta

# MoEngage API Configuration
MOENGAGE_CONFIG = {
    'workspace_id': '95PNUHBSYSLLJZ22PEOFMKF2',
    'data_api_key': 'Mj5JSGKcwYum9NKAGmGHJG_E',
    'campaign_api_key': '3XMHJ83D2X4V',
    'data_center': '01'
}

def test_segment_creation():
    """Test creating a simple segment"""
    
    print("🧪 Testing Segment Creation")
    print("=" * 50)
    
    # Test creating a simple UK segment
    segment_name = "UK_All_Users"
    description = "All UK users"
    filters = {
        "filter_operator": "and",
        "filters": [
            {
                "filter_type": "user_attributes",
                "name": "country",
                "data_type": "string",
                "operator": "in",
                "value": ["GB"],
                "negate": False,
                "case_sensitive": False
            }
        ]
    }
    
    url = f"https://api-{MOENGAGE_CONFIG['data_center']}.moengage.com/v3/custom-segments/"
    
    # Auth
    auth_string = f"{MOENGAGE_CONFIG['workspace_id']}:{MOENGAGE_CONFIG['data_api_key']}"
    encoded_auth = base64.b64encode(auth_string.encode()).decode()
    
    headers = {
        'Authorization': f'Basic {encoded_auth}',
        'Content-Type': 'application/json',
        'MOE-APPKEY': MOENGAGE_CONFIG['workspace_id']
    }
    
    payload = {
        "name": segment_name,
        "description": description,
        "included_filters": filters
    }
    
    print(f"📝 Creating segment: {segment_name}")
    print(f"🔗 URL: {url}")
    print(f"📋 Payload: {json.dumps(payload, indent=2)}")
    
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=15)
        print(f"📊 Status Code: {response.status_code}")
        print(f"📄 Response: {response.text}")
        
        if response.status_code in [200, 201]:
            data = response.json()
            segment_id = data.get('data', {}).get('id')
            print(f"✅ SUCCESS: Segment created with ID: {segment_id}")
            return True
        elif response.status_code == 409:
            print("⚠️  DUPLICATE: Segment with same filters already exists")
            try:
                error_data = response.json()
                existing_name = error_data.get('error', {}).get('existing_cs_name', 'Unknown')
                existing_id = error_data.get('error', {}).get('existing_cs_id', 'Unknown')
                print(f"🔄 Existing segment: {existing_name} (ID: {existing_id})")
                return True
            except:
                print("❌ Could not parse duplicate error response")
                return False
        else:
            print(f"❌ FAILED: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"💥 EXCEPTION: {e}")
        return False

def test_create_metrics_segments():
    """Test the actual create_metrics_segments function logic"""
    
    print("\n🧪 Testing create_metrics_segments Logic")
    print("=" * 50)
    
    segments = []
    countries = {'UK': 'GB', 'UAE': 'AE'}
    
    for country_name, country_code in countries.items():
        print(f"\n🌍 Processing {country_name} ({country_code})")
        
        # Test creating UK_All_Users segment
        segment_name = "UK_All_Users" if country_code == 'GB' else "UAE_All_Users"
        filters = {
            "filter_operator": "and",
            "filters": [
                {
                    "filter_type": "user_attributes",
                    "name": "country",
                    "data_type": "string",
                    "operator": "in",
                    "value": [country_code],
                    "negate": False,
                    "case_sensitive": False
                }
            ]
        }
        
        # Simulate the create_segment call
        result = create_segment_test(segment_name, f"All {country_name} users", filters)
        
        if 'error' not in result:
            result['display_name'] = f"{country_name} - All Users"
            result['field_name'] = f"{country_name.lower()}_total_users"
            segments.append(result)
            print(f"✅ Added segment: {result['display_name']}")
        else:
            print(f"❌ Failed to create segment: {result['error']}")
    
    print(f"\n📊 Total segments created: {len(segments)}")
    for segment in segments:
        print(f"  - {segment['display_name']} → {segment['field_name']}")
    
    return segments

def create_segment_test(segment_name, description, filters):
    """Test version of create_segment method"""
    
    url = f"https://api-{MOENGAGE_CONFIG['data_center']}.moengage.com/v3/custom-segments/"
    
    # Auth
    auth_string = f"{MOENGAGE_CONFIG['workspace_id']}:{MOENGAGE_CONFIG['data_api_key']}"
    encoded_auth = base64.b64encode(auth_string.encode()).decode()
    
    headers = {
        'Authorization': f'Basic {encoded_auth}',
        'Content-Type': 'application/json',
        'MOE-APPKEY': MOENGAGE_CONFIG['workspace_id']
    }
    
    payload = {
        "name": segment_name,
        "description": description,
        "included_filters": filters
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=15)
        
        if response.status_code in [200, 201]:
            data = response.json()
            segment_id = data['data']['id']
            return {
                'name': segment_name,
                'id': segment_id,
                'description': description,
                'url': f"https://dashboard-01.moengage.com/v4/segmentation/all-segments/custom-segments/{segment_id}",
                'status': 'created'
            }
        elif response.status_code == 409:
            # Segment with same filters already exists - reuse it
            try:
                error_data = response.json()
                existing_name = error_data.get('error', {}).get('existing_cs_name', segment_name)
                existing_id = error_data.get('error', {}).get('existing_cs_id', 'unknown')
                
                return {
                    'name': existing_name,
                    'id': existing_id,
                    'description': f"Reusing existing segment: {existing_name}",
                    'url': f"https://dashboard-01.moengage.com/v4/segmentation/all-segments/custom-segments/{existing_id}",
                    'status': 'reused'
                }
            except:
                return {
                    'name': f"Existing segment (similar to {segment_name})",
                    'id': 'unknown',
                    'description': "Reusing existing segment with same filters",
                    'url': "https://dashboard-01.moengage.com/v4/segmentation/all-segments/custom-segments",
                    'status': 'reused'
                }
        else:
            return {'error': f"API Error: {response.status_code} - {response.text}"}
            
    except requests.exceptions.Timeout:
        return {'error': f"Request timeout - MoEngage API took too long to respond"}
    except Exception as e:
        return {'error': f"Error creating segment: {str(e)}"}

if __name__ == "__main__":
    # Test 1: Simple segment creation
    success = test_segment_creation()
    
    # Test 2: Full create_metrics_segments logic
    if success:
        segments = test_create_metrics_segments()
        
        if segments:
            print("\n🎉 SUCCESS: Segments would be created successfully!")
        else:
            print("\n❌ FAILURE: No segments were created")
    else:
        print("\n❌ Basic segment creation failed, skipping full test")