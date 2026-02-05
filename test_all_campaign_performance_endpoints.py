#!/usr/bin/env python3
"""
Comprehensive test to find individual campaign performance metrics
Try every possible endpoint, authentication method, and data source
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

def get_sample_campaigns():
    """Get sample campaigns to test performance endpoints"""
    
    print("🔍 GETTING SAMPLE CAMPAIGNS FOR TESTING")
    print("=" * 50)
    
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
        "request_id": f"sample_campaigns_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
        "limit": 5,
        "page": 1,
        "campaign_fields": {
            "channels": ["PUSH", "EMAIL"]
        }
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        
        if response.status_code == 200:
            campaigns = response.json()
            print(f"✅ Found {len(campaigns)} sample campaigns")
            
            sample_campaigns = []
            for campaign in campaigns[:3]:  # Take first 3
                basic_details = campaign.get('basic_details', {})
                sample_campaigns.append({
                    'id': campaign.get('campaign_id'),
                    'name': basic_details.get('name', 'Unknown'),
                    'channel': campaign.get('channel'),
                    'status': campaign.get('status'),
                    'created_at': campaign.get('created_at'),
                    'sent_time': campaign.get('sent_time')
                })
                print(f"  • {sample_campaigns[-1]['name']} | {sample_campaigns[-1]['channel']} | {sample_campaigns[-1]['status']}")
            
            return sample_campaigns
        else:
            print(f"❌ Failed to get campaigns: {response.text}")
            return []
            
    except Exception as e:
        print(f"❌ Exception: {str(e)}")
        return []

def test_campaign_analytics_endpoints(campaign_id, campaign_name):
    """Test all possible campaign analytics endpoints"""
    
    print(f"\n🔍 TESTING CAMPAIGN ANALYTICS ENDPOINTS")
    print(f"Campaign: {campaign_name} ({campaign_id})")
    print("=" * 60)
    
    # Different authentication methods
    auth_methods = {
        'campaign_api': {
            'auth_string': f"{MOENGAGE_CONFIG['workspace_id']}:{MOENGAGE_CONFIG['campaign_api_key']}",
            'headers': {
                'MOE-APPKEY': MOENGAGE_CONFIG['workspace_id'],
                'APP_SECRET_KEY': MOENGAGE_CONFIG['campaign_api_key']
            }
        },
        'data_api': {
            'auth_string': f"{MOENGAGE_CONFIG['workspace_id']}:{MOENGAGE_CONFIG['data_api_key']}",
            'headers': {
                'MOE-APPKEY': MOENGAGE_CONFIG['workspace_id']
            }
        }
    }
    
    # All possible endpoints to test
    endpoints = [
        # Core services endpoints
        f"/core-services/v1/campaigns/{campaign_id}",
        f"/core-services/v1/campaigns/{campaign_id}/stats",
        f"/core-services/v1/campaigns/{campaign_id}/analytics",
        f"/core-services/v1/campaigns/{campaign_id}/performance",
        f"/core-services/v1/campaigns/{campaign_id}/metrics",
        f"/core-services/v1/campaigns/{campaign_id}/report",
        f"/core-services/v1/campaigns/{campaign_id}/summary",
        f"/core-services/v1/campaigns/{campaign_id}/details",
        
        # V1 endpoints
        f"/v1/campaigns/{campaign_id}",
        f"/v1/campaigns/{campaign_id}/stats",
        f"/v1/campaigns/{campaign_id}/analytics",
        f"/v1/campaigns/{campaign_id}/performance",
        f"/v1/campaigns/{campaign_id}/metrics",
        f"/v1/campaigns/{campaign_id}/report",
        
        # Campaign reports endpoints
        f"/campaign_reports/v1/campaigns/{campaign_id}",
        f"/campaign_reports/v1/campaigns/{campaign_id}/stats",
        f"/campaign_reports/v1/campaigns/{campaign_id}/analytics",
        f"/campaign_reports/v1/campaigns/{campaign_id}/performance",
        
        # Analytics endpoints
        f"/analytics/v1/campaigns/{campaign_id}",
        f"/analytics/v1/campaigns/{campaign_id}/stats",
        f"/analytics/v1/campaigns/{campaign_id}/performance",
        
        # Dashboard endpoints
        f"/dashboard/v1/campaigns/{campaign_id}",
        f"/dashboard/v1/campaigns/{campaign_id}/stats",
        f"/dashboard/v1/campaigns/{campaign_id}/analytics",
        
        # API endpoints
        f"/api/v1/campaigns/{campaign_id}",
        f"/api/v1/campaigns/{campaign_id}/stats",
        f"/api/v1/campaigns/{campaign_id}/analytics"
    ]
    
    working_endpoints = []
    
    for auth_name, auth_config in auth_methods.items():
        print(f"\n--- Testing with {auth_name.upper()} authentication ---")
        
        encoded_auth = base64.b64encode(auth_config['auth_string'].encode()).decode()
        base_headers = {
            'Authorization': f'Basic {encoded_auth}',
            'Content-Type': 'application/json'
        }
        base_headers.update(auth_config['headers'])
        
        for endpoint in endpoints:
            url = f"https://api-{MOENGAGE_CONFIG['data_center']}.moengage.com{endpoint}"
            
            try:
                response = requests.get(url, headers=base_headers, timeout=10)
                
                if response.status_code == 200:
                    print(f"✅ SUCCESS: {endpoint}")
                    data = response.json()
                    
                    # Look for performance metrics
                    performance_metrics = {}
                    if isinstance(data, dict):
                        for key, value in data.items():
                            if any(word in key.lower() for word in ['sent', 'delivered', 'open', 'click', 'conversion', 'bounce', 'unsubscribe']):
                                performance_metrics[key] = value
                    
                    if performance_metrics:
                        print(f"  📊 Performance metrics found:")
                        for key, value in performance_metrics.items():
                            if isinstance(value, (int, float)):
                                print(f"    {key}: {value:,}")
                            else:
                                print(f"    {key}: {type(value)}")
                    else:
                        print(f"  📋 Available keys: {list(data.keys()) if isinstance(data, dict) else 'Not a dict'}")
                    
                    working_endpoints.append({
                        'endpoint': endpoint,
                        'auth': auth_name,
                        'data': data,
                        'performance_metrics': performance_metrics
                    })
                    
                elif response.status_code == 404:
                    pass  # Expected for most endpoints
                elif response.status_code == 403:
                    print(f"🔒 FORBIDDEN: {endpoint}")
                elif response.status_code == 401:
                    print(f"🔑 UNAUTHORIZED: {endpoint}")
                else:
                    print(f"❓ {response.status_code}: {endpoint}")
                    
            except Exception as e:
                pass  # Skip connection errors
    
    return working_endpoints

def test_campaign_reports_api_individual(campaign_id, campaign_name):
    """Test if we can get individual campaign reports via Reports API"""
    
    print(f"\n🔍 TESTING INDIVIDUAL CAMPAIGN REPORTS API")
    print(f"Campaign: {campaign_name} ({campaign_id})")
    print("=" * 60)
    
    # Try to generate a report for specific campaign
    # This might be a different approach than the bulk reports we've been using
    
    # Generate signature for individual campaign report
    report_filename = f"campaign_{campaign_id}_report"
    signature_key = f"{MOENGAGE_CONFIG['workspace_id']}|{report_filename}|{MOENGAGE_CONFIG['campaign_api_key']}"
    signature = hashlib.sha256(signature_key.encode('utf-8')).hexdigest()
    
    auth_string = f"{MOENGAGE_CONFIG['workspace_id']}:{MOENGAGE_CONFIG['campaign_api_key']}"
    encoded_auth = base64.b64encode(auth_string.encode()).decode()
    
    headers = {
        'Authorization': f'Basic {encoded_auth}',
        'MOE-APPKEY': MOENGAGE_CONFIG['workspace_id'],
        'Signature': signature
    }
    
    # Try different report endpoints
    report_endpoints = [
        f"/campaign_reports/rest_api/{MOENGAGE_CONFIG['workspace_id']}/campaign_{campaign_id}",
        f"/campaign_reports/rest_api/{MOENGAGE_CONFIG['workspace_id']}/{campaign_id}",
        f"/campaign_reports/v1/{MOENGAGE_CONFIG['workspace_id']}/campaign_{campaign_id}",
        f"/reports/v1/campaigns/{campaign_id}",
        f"/reports/campaigns/{campaign_id}"
    ]
    
    for endpoint in report_endpoints:
        url = f"https://api-{MOENGAGE_CONFIG['data_center']}.moengage.com{endpoint}"
        
        try:
            print(f"Testing: {endpoint}")
            response = requests.get(url, headers=headers, timeout=15)
            
            if response.status_code == 200:
                print(f"✅ SUCCESS: Individual campaign report available!")
                print(f"  Content-Type: {response.headers.get('content-type', 'Unknown')}")
                print(f"  Content-Length: {len(response.content)} bytes")
                
                # Try to parse if it's JSON
                try:
                    data = response.json()
                    print(f"  📊 JSON data available: {list(data.keys())}")
                    return data
                except:
                    print(f"  📄 Binary/text data (likely CSV/ZIP)")
                    return response.content
                    
            elif response.status_code == 404:
                print(f"  ❌ 404 - Not found")
            elif response.status_code == 403:
                print(f"  🔒 403 - Forbidden")
            else:
                print(f"  ❓ {response.status_code}")
                
        except Exception as e:
            print(f"  ❌ Exception: {str(e)}")
    
    return None

def test_dashboard_api_endpoints(campaign_id, campaign_name):
    """Test dashboard-style API endpoints that might have analytics"""
    
    print(f"\n🔍 TESTING DASHBOARD API ENDPOINTS")
    print(f"Campaign: {campaign_name} ({campaign_id})")
    print("=" * 60)
    
    auth_string = f"{MOENGAGE_CONFIG['workspace_id']}:{MOENGAGE_CONFIG['campaign_api_key']}"
    encoded_auth = base64.b64encode(auth_string.encode()).decode()
    
    headers = {
        'Authorization': f'Basic {encoded_auth}',
        'MOE-APPKEY': MOENGAGE_CONFIG['workspace_id'],
        'APP_SECRET_KEY': MOENGAGE_CONFIG['campaign_api_key'],
        'Content-Type': 'application/json'
    }
    
    # Dashboard-style endpoints that might exist
    dashboard_endpoints = [
        f"/dashboard-api/v1/campaigns/{campaign_id}/analytics",
        f"/dashboard-api/v1/campaigns/{campaign_id}/stats",
        f"/dashboard-api/v1/campaigns/{campaign_id}/performance",
        f"/internal/v1/campaigns/{campaign_id}/stats",
        f"/internal/v1/campaigns/{campaign_id}/analytics",
        f"/admin/v1/campaigns/{campaign_id}/stats",
        f"/metrics/v1/campaigns/{campaign_id}",
        f"/stats/v1/campaigns/{campaign_id}",
        f"/performance/v1/campaigns/{campaign_id}"
    ]
    
    working_endpoints = []
    
    for endpoint in dashboard_endpoints:
        url = f"https://api-{MOENGAGE_CONFIG['data_center']}.moengage.com{endpoint}"
        
        try:
            response = requests.get(url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                print(f"✅ SUCCESS: {endpoint}")
                try:
                    data = response.json()
                    print(f"  📊 Data available: {list(data.keys()) if isinstance(data, dict) else 'Not a dict'}")
                    working_endpoints.append({'endpoint': endpoint, 'data': data})
                except:
                    print(f"  📄 Non-JSON response")
                    working_endpoints.append({'endpoint': endpoint, 'data': response.text})
                    
            elif response.status_code == 404:
                pass  # Expected
            elif response.status_code == 403:
                print(f"🔒 FORBIDDEN: {endpoint}")
            elif response.status_code == 401:
                print(f"🔑 UNAUTHORIZED: {endpoint}")
                
        except Exception as e:
            pass  # Skip connection errors
    
    return working_endpoints

def test_alternative_data_sources():
    """Test alternative ways to get campaign performance data"""
    
    print(f"\n🔍 TESTING ALTERNATIVE DATA SOURCES")
    print("=" * 60)
    
    # Test if we can get aggregated stats that might include campaign breakdowns
    auth_string = f"{MOENGAGE_CONFIG['workspace_id']}:{MOENGAGE_CONFIG['campaign_api_key']}"
    encoded_auth = base64.b64encode(auth_string.encode()).decode()
    
    headers = {
        'Authorization': f'Basic {encoded_auth}',
        'MOE-APPKEY': MOENGAGE_CONFIG['workspace_id'],
        'APP_SECRET_KEY': MOENGAGE_CONFIG['campaign_api_key'],
        'Content-Type': 'application/json'
    }
    
    # Alternative endpoints that might have campaign performance data
    alternative_endpoints = [
        "/core-services/v1/analytics/campaigns",
        "/core-services/v1/stats/campaigns",
        "/core-services/v1/performance/campaigns",
        "/core-services/v1/reports/campaigns",
        "/v1/analytics/campaigns",
        "/v1/stats/campaigns",
        "/v1/performance/campaigns",
        "/analytics/campaigns",
        "/stats/campaigns",
        "/performance/campaigns"
    ]
    
    working_endpoints = []
    
    for endpoint in alternative_endpoints:
        url = f"https://api-{MOENGAGE_CONFIG['data_center']}.moengage.com{endpoint}"
        
        # Try both GET and POST
        for method in ['GET', 'POST']:
            try:
                if method == 'GET':
                    response = requests.get(url, headers=headers, timeout=10)
                else:
                    payload = {
                        "request_id": f"alt_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                        "date_range": {
                            "from_date": "2026-02-01",
                            "to_date": "2026-02-28"
                        }
                    }
                    response = requests.post(url, json=payload, headers=headers, timeout=10)
                
                if response.status_code == 200:
                    print(f"✅ SUCCESS: {method} {endpoint}")
                    try:
                        data = response.json()
                        print(f"  📊 Data available: {list(data.keys()) if isinstance(data, dict) else 'Not a dict'}")
                        working_endpoints.append({'endpoint': endpoint, 'method': method, 'data': data})
                    except:
                        print(f"  📄 Non-JSON response")
                        
                elif response.status_code == 404:
                    pass  # Expected
                elif response.status_code == 403:
                    print(f"🔒 FORBIDDEN: {method} {endpoint}")
                elif response.status_code == 401:
                    print(f"🔑 UNAUTHORIZED: {method} {endpoint}")
                    
            except Exception as e:
                pass  # Skip connection errors
    
    return working_endpoints

def main():
    """Main function to test all possible approaches"""
    
    print("🚀 COMPREHENSIVE CAMPAIGN PERFORMANCE METRICS DISCOVERY")
    print("=" * 80)
    
    # Get sample campaigns
    sample_campaigns = get_sample_campaigns()
    
    if not sample_campaigns:
        print("❌ No sample campaigns available for testing")
        return
    
    all_working_endpoints = []
    
    # Test each sample campaign
    for campaign in sample_campaigns[:2]:  # Test first 2 campaigns
        campaign_id = campaign['id']
        campaign_name = campaign['name']
        
        print(f"\n" + "="*80)
        print(f"🎯 TESTING CAMPAIGN: {campaign_name}")
        print(f"ID: {campaign_id} | Channel: {campaign['channel']} | Status: {campaign['status']}")
        print("="*80)
        
        # Test 1: Standard analytics endpoints
        analytics_endpoints = test_campaign_analytics_endpoints(campaign_id, campaign_name)
        all_working_endpoints.extend(analytics_endpoints)
        
        # Test 2: Individual campaign reports
        individual_report = test_campaign_reports_api_individual(campaign_id, campaign_name)
        if individual_report:
            all_working_endpoints.append({
                'type': 'individual_report',
                'campaign_id': campaign_id,
                'data': individual_report
            })
        
        # Test 3: Dashboard API endpoints
        dashboard_endpoints = test_dashboard_api_endpoints(campaign_id, campaign_name)
        all_working_endpoints.extend(dashboard_endpoints)
    
    # Test 4: Alternative data sources
    alternative_endpoints = test_alternative_data_sources()
    all_working_endpoints.extend(alternative_endpoints)
    
    print(f"\n" + "="*80)
    print("📊 FINAL RESULTS SUMMARY")
    print("="*80)
    
    if all_working_endpoints:
        print(f"✅ FOUND {len(all_working_endpoints)} WORKING ENDPOINTS!")
        
        performance_endpoints = []
        for endpoint_info in all_working_endpoints:
            if endpoint_info.get('performance_metrics'):
                performance_endpoints.append(endpoint_info)
        
        if performance_endpoints:
            print(f"🎯 PERFORMANCE METRICS FOUND: {len(performance_endpoints)} endpoints")
            for endpoint_info in performance_endpoints:
                print(f"  • {endpoint_info['endpoint']} ({endpoint_info['auth']})")
                for metric, value in endpoint_info['performance_metrics'].items():
                    print(f"    - {metric}: {value}")
        else:
            print(f"📋 Working endpoints found, but no performance metrics yet")
            print(f"Available endpoints:")
            for endpoint_info in all_working_endpoints:
                endpoint_name = endpoint_info.get('endpoint', endpoint_info.get('type', 'Unknown'))
                print(f"  • {endpoint_name}")
        
        print(f"\n💡 NEXT STEPS:")
        if performance_endpoints:
            print("🎯 IMPLEMENT PERFORMANCE ENDPOINTS!")
            print("  1. Integrate working performance endpoints")
            print("  2. Extract sent/delivered counts")
            print("  3. Replace Reports API completely")
        else:
            print("🔍 INVESTIGATE WORKING ENDPOINTS:")
            print("  1. Analyze data structure of working endpoints")
            print("  2. Look for nested performance data")
            print("  3. Contact MoEngage support with specific endpoint findings")
    else:
        print("❌ NO WORKING PERFORMANCE ENDPOINTS FOUND")
        print("💡 RECOMMENDATIONS:")
        print("  1. Contact MoEngage support for campaign analytics API access")
        print("  2. Request individual campaign performance endpoints")
        print("  3. Proceed with Campaign Details API + campaign counts approach")
        print("  4. Wait for Stats API to be enabled")

if __name__ == "__main__":
    main()