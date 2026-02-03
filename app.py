#!/usr/bin/env python3
"""
MTU Automation Web Interface
Free web app for creating MoEngage segments and calculating MTU
"""

from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
import requests
import base64
from datetime import datetime, timedelta
import json
import os
import gspread
from google.oauth2.service_account import Credentials
import random
import string
import hashlib
import zipfile
import csv
import io

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'mtu-automation-secret-key-2026')

# Make datetime available in templates
@app.context_processor
def inject_datetime():
    return {'datetime': datetime, 'timedelta': timedelta}

# Configuration
MOENGAGE_CONFIG = {
    'workspace_id': '95PNUHBSYSLLJZ22PEOFMKF2',
    'data_api_key': 'Mj5JSGKcwYum9NKAGmGHJG_E',
    'campaign_api_key': '3XMHJ83D2X4V',
    'data_center': '01'
}

GOOGLE_SHEET_ID = "1A30FfO319eiKW0c6zHj2lwr04WLE0fL6eLteZf4CvHM"

class MTUWebAutomation:
    def __init__(self):
        self.created_segments = []
        # Don't initialize Google Sheets in constructor to avoid blocking the app
    
    def get_date_range(self, end_date_str):
        """Get date range from month start to selected date"""
        try:
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d')
            yesterday = datetime.now() - timedelta(days=1)
            
            if end_date > yesterday:
                raise ValueError(f"End date cannot exceed {yesterday.strftime('%Y-%m-%d')}")
            
            start_date = end_date.replace(day=1)
            return start_date, end_date
            
        except ValueError as e:
            return None, None
    
    def create_segment(self, segment_name, description, filters):
        """Create a segment using MoEngage Custom Segment API"""
        try:
            url = f"https://api-{MOENGAGE_CONFIG['data_center']}.moengage.com/v3/custom-segments/"
            
            # Auth
            auth_string = f"{MOENGAGE_CONFIG['workspace_id']}:{MOENGAGE_CONFIG['data_api_key']}"
            encoded_auth = base64.b64encode(auth_string.encode()).decode()
            
            headers = {
                'Authorization': f'Basic {encoded_auth}',
                'Content-Type': 'application/json',
                'MOE-APPKEY': MOENGAGE_CONFIG['workspace_id']
            }
            
            # Add random component to description to avoid duplicate detection
            random_id = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
            unique_description = f"{description} [ID: {random_id}]"
            
            payload = {
                "name": segment_name,
                "description": unique_description,
                "included_filters": filters
            }
            
            # Reduced timeout to avoid gateway timeouts
            response = requests.post(url, json=payload, headers=headers, timeout=15)
            
            if response.status_code in [200, 201]:
                data = response.json()
                segment_id = data['data']['id']
                segment_info = {
                    'name': segment_name,
                    'id': segment_id,
                    'description': unique_description,
                    'url': f"https://dashboard-01.moengage.com/v4/segmentation/all-segments/custom-segments/{segment_id}",
                    'status': 'created'
                }
                self.created_segments.append(segment_info)
                return segment_info
            elif response.status_code == 409:
                # Segment with same filters already exists - reuse it
                try:
                    error_data = response.json()
                    existing_name = error_data.get('error', {}).get('existing_cs_name', 'Unknown')
                    existing_id = error_data.get('error', {}).get('existing_cs_id', 'Unknown')
                    
                    segment_info = {
                        'name': existing_name,
                        'id': existing_id,
                        'description': f"Reusing existing segment: {existing_name}",
                        'url': f"https://dashboard-01.moengage.com/v4/segmentation/all-segments/custom-segments/{existing_id}",
                        'status': 'reused'
                    }
                    self.created_segments.append(segment_info)
                    return segment_info
                except:
                    # Fallback if we can't parse the error
                    segment_info = {
                        'name': f"Existing segment (similar to {segment_name})",
                        'id': 'unknown',
                        'description': "Reusing existing segment with same filters",
                        'url': "https://dashboard-01.moengage.com/v4/segmentation/all-segments/custom-segments",
                        'status': 'reused'
                    }
                    self.created_segments.append(segment_info)
                    return segment_info
            else:
                return {'error': f"API Error: {response.status_code} - {response.text}"}
                
        except requests.exceptions.Timeout:
            return {'error': f"Request timeout - MoEngage API took too long to respond"}
        except Exception as e:
            return {'error': f"Error creating segment: {str(e)}"}
    
    def create_all_mtu_segments(self, end_date):
        """Create all segments needed for MTU calculations"""
        
        # Get date range
        start_date, end_date_obj = self.get_date_range(end_date)
        if not start_date:
            return {'error': 'Invalid date range'}
        
        start_date_str = start_date.strftime('%Y-%m-%d')
        end_date_str = end_date_obj.strftime('%Y-%m-%d')
        
        countries = {'UK': 'GB', 'UAE': 'AE'}
        channels = ['push', 'email']
        
        self.created_segments = []
        failed_segments = []
        
        for country_name, country_code in countries.items():
            
            # 1. All users in country
            segment_name = f"Automated_{country_code}_AllUsers_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
            description = f"All {country_name} users for MTU calculation"
            
            # Revert to simple filters - don't try to make them unique
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
            
            result = self.create_segment(segment_name, description, filters)
            if 'error' in result:
                failed_segments.append(f"{segment_name}: {result['error']}")
                # Continue with other segments instead of stopping
            
            # 2. Active users in country (60 days)
            segment_name = f"Automated_{country_code}_Active60d_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
            description = f"{country_name} users who transacted in last 60 days"
            
            # Calculate date range
            end_date_calc = datetime.now()
            start_date_calc = end_date_calc - timedelta(days=60)
            
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
                    },
                    {
                        "filter_type": "actions",
                        "attributes": {
                            "filter_operator": "and",
                            "filters": []
                        },
                        "executed": True,
                        "primary_time_range": {
                            "type": "between",
                            "value": start_date_calc.strftime('%Y-%m-%dT00:00:00.000Z'),
                            "value1": end_date_calc.strftime('%Y-%m-%dT23:59:59.999Z'),
                            "value_type": "absolute",
                            "period_unit": "days"
                        },
                        "action_name": "ORDER",
                        "execution": {
                            "count": 1,
                            "type": "atleast"
                        }
                    }
                ]
            }
            
            result = self.create_segment(segment_name, description, filters)
            if 'error' in result:
                failed_segments.append(f"{segment_name}: {result['error']}")
                # Continue with other segments
            
            # 3. Users who received communications (for each channel)
            for channel in channels:
                event_name = "MOE_EMAIL_SENT" if channel == "email" else "MOE_PUSH_SENT"
                
                segment_name = f"Automated_{country_code}_{channel.title()}Received_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
                description = f"{country_name} users who received {channel} from {start_date_str} to {end_date_str}"
                
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
                        },
                        {
                            "filter_type": "actions",
                            "attributes": {
                                "filter_operator": "and",
                                "filters": []
                            },
                            "executed": True,
                            "primary_time_range": {
                                "type": "between",
                                "value": f"{start_date_str}T00:00:00.000Z",
                                "value1": f"{end_date_str}T23:59:59.999Z",
                                "value_type": "absolute",
                                "period_unit": "days"
                            },
                            "action_name": event_name,
                            "execution": {
                                "count": 1,
                                "type": "atleast"
                            }
                        }
                    ]
                }
                
                result = self.create_segment(segment_name, description, filters)
                if 'error' in result:
                    failed_segments.append(f"{segment_name}: {result['error']}")
                    # Continue with other segments
                
                # 4. Active users who received communications
                segment_name = f"Automated_{country_code}_{channel.title()}Active60d_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
                description = f"{country_name} active users (60d) who received {channel} from {start_date_str} to {end_date_str}"
                
                # Calculate active period
                active_end = datetime.now()
                active_start = active_end - timedelta(days=60)
                
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
                        },
                        {
                            "filter_type": "actions",
                            "attributes": {
                                "filter_operator": "and",
                                "filters": []
                            },
                            "executed": True,
                            "primary_time_range": {
                                "type": "between",
                                "value": f"{start_date_str}T00:00:00.000Z",
                                "value1": f"{end_date_str}T23:59:59.999Z",
                                "value_type": "absolute",
                                "period_unit": "days"
                            },
                            "action_name": event_name,
                            "execution": {
                                "count": 1,
                                "type": "atleast"
                            }
                        },
                        {
                            "filter_type": "actions",
                            "attributes": {
                                "filter_operator": "and",
                                "filters": []
                            },
                            "executed": True,
                            "primary_time_range": {
                                "type": "between",
                                "value": active_start.strftime('%Y-%m-%dT00:00:00.000Z'),
                                "value1": active_end.strftime('%Y-%m-%dT23:59:59.999Z'),
                                "value_type": "absolute",
                                "period_unit": "days"
                            },
                            "action_name": "ORDER",
                            "execution": {
                                "count": 1,
                                "type": "atleast"
                            }
                        }
                    ]
                }
                
                result = self.create_segment(segment_name, description, filters)
                if 'error' in result:
                    failed_segments.append(f"{segment_name}: {result['error']}")
                    # Continue with other segments
        
        # Return results even if some segments failed
        response = {
            'success': True,
            'segments': self.created_segments,
            'period': f"{start_date_str} to {end_date_str}",
            'dashboard_url': 'https://dashboard-01.moengage.com/v4/segmentation/all-segments/custom-segments'
        }
        
        if failed_segments:
            response['warnings'] = failed_segments
        
        return response

class CommsPerUserAutomation:
    def __init__(self):
        self.downloaded_reports = {}
        
    def get_date_range(self, end_date_str):
        """Get date range from month start to selected date"""
        try:
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d')
            yesterday = datetime.now() - timedelta(days=1)
            
            if end_date > yesterday:
                raise ValueError(f"End date cannot exceed {yesterday.strftime('%Y-%m-%d')}")
            
            start_date = end_date.replace(day=1)
            return start_date, end_date
            
        except ValueError as e:
            return None, None
        
    def get_date_range(self, end_date_str):
        """Get date range from month start to selected date"""
        try:
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d')
            yesterday = datetime.now() - timedelta(days=1)
            
            if end_date > yesterday:
                raise ValueError(f"End date cannot exceed {yesterday.strftime('%Y-%m-%d')}")
            
            start_date = end_date.replace(day=1)
            return start_date, end_date
            
        except ValueError as e:
            return None, None
    
    def download_report(self, report_filename, start_date=None, end_date=None):
        """Download campaign report from MoEngage with date parameters"""
        
        # Generate signature: App_ID|FILENAME|SECRET_KEY
        signature_key = f"{MOENGAGE_CONFIG['workspace_id']}|{report_filename}|{MOENGAGE_CONFIG['campaign_api_key']}"
        signature = hashlib.sha256(signature_key.encode('utf-8')).hexdigest()
        
        url = f"https://api-{MOENGAGE_CONFIG['data_center']}.moengage.com/campaign_reports/rest_api/{MOENGAGE_CONFIG['workspace_id']}/{report_filename}"
        
        # Headers
        auth_string = f"{MOENGAGE_CONFIG['workspace_id']}:{MOENGAGE_CONFIG['campaign_api_key']}"
        encoded_auth = base64.b64encode(auth_string.encode()).decode()
        
        headers = {
            'Authorization': f'Basic {encoded_auth}',
            'MOE-APPKEY': MOENGAGE_CONFIG['workspace_id'],
            'Signature': signature
        }
        
        # Add date parameters if provided
        params = {}
        if start_date and end_date:
            params['start_date'] = start_date
            params['end_date'] = end_date
        
        try:
            print(f"📥 Downloading report: {report_filename}")
            if params:
                print(f"📅 Date range: {start_date} to {end_date}")
            
            response = requests.get(url, headers=headers, params=params, timeout=30)
            
            if response.status_code == 200:
                print(f"✅ Report downloaded successfully")
                return response.content
            else:
                print(f"❌ API Error: {response.status_code} - {response.text}")
                return {'error': f"API Error: {response.status_code} - {response.text}"}
                
        except Exception as e:
            print(f"❌ Download error: {str(e)}")
            return {'error': f"Error downloading report: {str(e)}"}
    
    def parse_report(self, zip_content, report_type):
        """Parse report and extract communication counts by country"""
        
        if not zip_content or isinstance(zip_content, dict):
            return {'error': 'No report data available'}
        
        try:
            # Extract ZIP content
            with zipfile.ZipFile(io.BytesIO(zip_content)) as zip_file:
                csv_files = [f for f in zip_file.namelist() if f.endswith('.csv')]
                
                if not csv_files:
                    return {'error': 'No CSV files found in report'}
                
                # Read the first CSV file
                csv_filename = csv_files[0]
                with zip_file.open(csv_filename) as csv_file:
                    csv_content = csv_file.read().decode('utf-8')
                
                # Parse CSV
                csv_reader = csv.DictReader(io.StringIO(csv_content))
                
                uk_total = 0
                uae_total = 0
                
                for row in csv_reader:
                    campaign_name = row.get('Campaign Name', '').lower()
                    
                    # Determine sent count based on report type
                    if 'pn' in report_type.lower():
                        sent_count = int(row.get('All Platform Sent', 0) or 0)
                    else:  # Email
                        sent_count = int(row.get('Sent', 0) or 0)
                    
                    # Filter by country
                    if 'uk' in campaign_name:
                        uk_total += sent_count
                    elif 'uae' in campaign_name:
                        uae_total += sent_count
                
                return {
                    'uk_total': uk_total,
                    'uae_total': uae_total,
                    'csv_filename': csv_filename,
                    'total_rows': len(list(csv.DictReader(io.StringIO(csv_content))))
                }
                
        except Exception as e:
            return {'error': f"Error parsing report: {str(e)}"}
    
    def get_user_counts(self, end_date_str):
        """Get user counts using Segmentation API"""
        
        # Get date range
        start_date, end_date = self.get_date_range(end_date_str)
        if not start_date:
            return {'error': 'Invalid date range'}
        
        start_date_str = start_date.strftime('%Y-%m-%d')
        end_date_str = end_date.strftime('%Y-%m-%d')
        
        countries = {'UK': 'GB', 'UAE': 'AE'}
        user_counts = {}
        
        for country_name, country_code in countries.items():
            
            # 1. Create segment for total users in country
            total_segment_name = f"CommsCalc_{country_code}_Total_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
            total_filters = {
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
            
            total_segment = self.create_segment(
                total_segment_name,
                f"Total {country_name} users for Communications Per User calculation",
                total_filters
            )
            
            if 'error' in total_segment:
                return {'error': f"Failed to create total users segment for {country_name}: {total_segment['error']}"}
            
            # 2. Create segment for users who transacted in the period
            transacted_segment_name = f"CommsCalc_{country_code}_Transacted_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
            transacted_filters = {
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
                    },
                    {
                        "filter_type": "actions",
                        "attributes": {
                            "filter_operator": "and",
                            "filters": []
                        },
                        "executed": True,
                        "primary_time_range": {
                            "type": "between",
                            "value": f"{start_date_str}T00:00:00.000Z",
                            "value1": f"{end_date_str}T23:59:59.999Z",
                            "value_type": "absolute",
                            "period_unit": "days"
                        },
                        "action_name": "ORDER",
                        "execution": {
                            "count": 1,
                            "type": "atleast"
                        }
                    }
                ]
            }
            
            transacted_segment = self.create_segment(
                transacted_segment_name,
                f"{country_name} users who transacted from {start_date_str} to {end_date_str}",
                transacted_filters
            )
            
            if 'error' in transacted_segment:
                return {'error': f"Failed to create transacted users segment for {country_name}: {transacted_segment['error']}"}
            
            # Store segment info for manual count retrieval
            user_counts[f'{country_name.lower()}_total_segment'] = {
                'name': total_segment['name'],
                'id': total_segment['id'],
                'url': total_segment['url']
            }
            user_counts[f'{country_name.lower()}_transacted_segment'] = {
                'name': transacted_segment['name'],
                'id': transacted_segment['id'],
                'url': transacted_segment['url']
            }
        
        # Note: MoEngage API doesn't return segment counts automatically
        # User will need to manually get counts from dashboard
        return {
            'segments_created': True,
            'uk_total_segment': user_counts['uk_total_segment'],
            'uk_transacted_segment': user_counts['uk_transacted_segment'],
            'uae_total_segment': user_counts['uae_total_segment'],
            'uae_transacted_segment': user_counts['uae_transacted_segment'],
            'period': f"{start_date_str} to {end_date_str}",
            'instructions': "Please visit the segment URLs to get the user counts and enter them manually."
        }
    
    def create_segment(self, segment_name, description, filters):
        """Create a segment using MoEngage Custom Segment API"""
        try:
            url = f"https://api-{MOENGAGE_CONFIG['data_center']}.moengage.com/v3/custom-segments/"
            
            # Auth
            auth_string = f"{MOENGAGE_CONFIG['workspace_id']}:{MOENGAGE_CONFIG['data_api_key']}"
            encoded_auth = base64.b64encode(auth_string.encode()).decode()
            
            headers = {
                'Authorization': f'Basic {encoded_auth}',
                'Content-Type': 'application/json',
                'MOE-APPKEY': MOENGAGE_CONFIG['workspace_id']
            }
            
            # Add random component to description to avoid duplicate detection
            random_id = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
            unique_description = f"{description} [ID: {random_id}]"
            
            payload = {
                "name": segment_name,
                "description": unique_description,
                "included_filters": filters
            }
            
            response = requests.post(url, json=payload, headers=headers, timeout=15)
            
            if response.status_code in [200, 201]:
                data = response.json()
                segment_id = data['data']['id']
                return {
                    'name': segment_name,
                    'id': segment_id,
                    'description': unique_description,
                    'url': f"https://dashboard-01.moengage.com/v4/segmentation/all-segments/custom-segments/{segment_id}",
                    'status': 'created'
                }
            elif response.status_code == 409:
                # Segment already exists - reuse it
                try:
                    error_data = response.json()
                    existing_name = error_data.get('error', {}).get('existing_cs_name', 'Unknown')
                    existing_id = error_data.get('error', {}).get('existing_cs_id', 'Unknown')
                    
                    return {
                        'name': existing_name,
                        'id': existing_id,
                        'description': f"Reusing existing segment: {existing_name}",
                        'url': f"https://dashboard-01.moengage.com/v4/segmentation/all-segments/custom-segments/{existing_id}",
                        'status': 'reused'
                    }
                except:
                    return {'error': f"Segment conflict but couldn't parse existing segment info"}
            else:
                return {'error': f"API Error: {response.status_code} - {response.text}"}
                
        except Exception as e:
            return {'error': f"Error creating segment: {str(e)}"}
    
    def calculate_comms_per_user(self, end_date_str, user_counts_manual=None):
        """Calculate communications per user metrics"""
        
        # Get date range for API parameters
        start_date, end_date = self.get_date_range(end_date_str)
        if not start_date:
            return {'error': 'Invalid date range'}
        
        # Format dates for API (YYYY-MM-DD format)
        start_date_api = start_date.strftime('%Y-%m-%d')
        end_date_api = end_date.strftime('%Y-%m-%d')
        
        # If no manual user counts provided, create segments first
        if not user_counts_manual:
            segment_result = self.get_user_counts(end_date_str)
            if 'error' in segment_result:
                return segment_result
            
            # Return segment info for manual count collection
            return {
                'step': 'segments_created',
                'segments': segment_result,
                'next_action': 'Please visit the segment URLs, get the user counts, and proceed to step 2'
            }
        
        # USE REPORTS API (current approach)
        print("📊 Using Reports API (fixed date ranges)")
        
        # Static report filenames (as configured in MoEngage)
        # NOTE: These reports have FIXED date ranges and cannot be changed via API
        # Current reports appear to cover: January 1-2, 2026 (based on campaign analysis)
        # For different date ranges, new reports must be created in MoEngage dashboard
        reports = {
            'transactional_pn': "API_TX_PN_20260202",      # Covers: ~Jan 1-2, 2026
            'transactional_email': "API_TX_Email_20260202", # Covers: ~Jan 1-2, 2026
            'promotional_pn': "API_PR_PN_20260202",        # Covers: ~Jan 1-2, 2026
            'promotional_email': "API_PR_Email_20260202"   # Covers: ~Jan 1-2, 2026
        }
        
        # Download and parse all reports with date parameters (though they don't work)
        report_data = {}
        
        for report_type, filename in reports.items():
            zip_content = self.download_report(filename, start_date_api, end_date_api)
            
            if isinstance(zip_content, dict) and 'error' in zip_content:
                return zip_content
            
            parsed_data = self.parse_report(zip_content, report_type)
            
            if 'error' in parsed_data:
                return parsed_data
            
            report_data[report_type] = parsed_data
        
        # Use manual user counts
        user_counts = user_counts_manual
        
        # Calculate metrics
        results = {
            'period': f"{start_date_api} to {end_date_api} (Requested)",
            'actual_period': "~January 1-2, 2026 (Report limitation)",
            'data_source': 'Reports API (Fixed dates)',
            'uk': {},
            'uae': {}
        }
        
        # UK Calculations
        results['uk'] = {
            'transactional_pn': round(report_data['transactional_pn']['uk_total'] / user_counts['uk_transacted_users'], 4) if user_counts['uk_transacted_users'] > 0 else 0,
            'transactional_email': round(report_data['transactional_email']['uk_total'] / user_counts['uk_transacted_users'], 4) if user_counts['uk_transacted_users'] > 0 else 0,
            'promotional_pn': round(report_data['promotional_pn']['uk_total'] / user_counts['uk_total_users'], 4) if user_counts['uk_total_users'] > 0 else 0,
            'promotional_email': round(report_data['promotional_email']['uk_total'] / user_counts['uk_total_users'], 4) if user_counts['uk_total_users'] > 0 else 0,
            'total_users': user_counts['uk_total_users'],
            'transacted_users': user_counts['uk_transacted_users'],
            'raw_counts': {
                'transactional_pn': report_data['transactional_pn']['uk_total'],
                'transactional_email': report_data['transactional_email']['uk_total'],
                'promotional_pn': report_data['promotional_pn']['uk_total'],
                'promotional_email': report_data['promotional_email']['uk_total']
            }
        }
        
        # UAE Calculations
        results['uae'] = {
            'transactional_pn': round(report_data['transactional_pn']['uae_total'] / user_counts['uae_transacted_users'], 4) if user_counts['uae_transacted_users'] > 0 else 0,
            'transactional_email': round(report_data['transactional_email']['uae_total'] / user_counts['uae_transacted_users'], 4) if user_counts['uae_transacted_users'] > 0 else 0,
            'promotional_pn': round(report_data['promotional_pn']['uae_total'] / user_counts['uae_total_users'], 4) if user_counts['uae_total_users'] > 0 else 0,
            'promotional_email': round(report_data['promotional_email']['uae_total'] / user_counts['uae_total_users'], 4) if user_counts['uae_total_users'] > 0 else 0,
            'total_users': user_counts['uae_total_users'],
            'transacted_users': user_counts['uae_transacted_users'],
            'raw_counts': {
                'transactional_pn': report_data['transactional_pn']['uae_total'],
                'transactional_email': report_data['transactional_email']['uae_total'],
                'promotional_pn': report_data['promotional_pn']['uae_total'],
                'promotional_email': report_data['promotional_email']['uae_total']
            }
        }
        
        return results

# Initialize automations
automation = MTUWebAutomation()
comms_automation = CommsPerUserAutomation()

@app.route('/')
def index():
    """Home page with date input"""
    try:
        return render_template('index.html')
    except Exception as e:
        return f"Error loading home page: {str(e)}", 500

@app.route('/health')
def health_check():
    """Health check endpoint"""
    return {"status": "ok", "message": "MTU Automation is running"}, 200

@app.route('/test')
def test_route():
    """Simple test route"""
    return "<h1>MTU Automation Test</h1><p>If you see this, the Flask app is working!</p>"

@app.route('/create-segments', methods=['POST'])
def create_segments():
    """Create MTU segments"""
    try:
        end_date = request.form.get('end_date')
        
        if not end_date:
            flash('Please select an end date', 'error')
            return redirect(url_for('index'))
        
        result = automation.create_all_mtu_segments(end_date)
        
        if 'error' in result:
            flash(f'Error: {result["error"]}', 'error')
            return redirect(url_for('index'))
        
        # Check if we have any segments (even if some failed)
        if result.get('segments'):
            return render_template('segments_created.html', 
                                 segments=result['segments'],
                                 period=result['period'],
                                 dashboard_url=result['dashboard_url'])
        else:
            flash('No segments were created. Please try again.', 'error')
            return redirect(url_for('index'))
        
    except Exception as e:
        flash(f'Unexpected error: {str(e)}', 'error')
        return redirect(url_for('index'))

@app.route('/comms-per-user')
def comms_per_user_form():
    """Show Communications Per User calculation form"""
    return render_template('comms_per_user.html')

@app.route('/calculate-comms-per-user', methods=['POST'])
def calculate_comms_per_user():
    """Calculate Communications Per User metrics"""
    try:
        end_date = request.form.get('end_date')
        
        if not end_date:
            flash('Please select an end date', 'error')
            return redirect(url_for('comms_per_user_form'))
        
        # Check if this is step 2 (with manual user counts)
        if 'uk_total_users' in request.form:
            # Step 2: Calculate with manual user counts
            try:
                user_counts = {
                    'uk_total_users': int(request.form.get('uk_total_users', 0)),
                    'uk_transacted_users': int(request.form.get('uk_transacted_users', 0)),
                    'uae_total_users': int(request.form.get('uae_total_users', 0)),
                    'uae_transacted_users': int(request.form.get('uae_transacted_users', 0))
                }
                
                result = comms_automation.calculate_comms_per_user(end_date, user_counts)
                
                if 'error' in result:
                    flash(f'Error: {result["error"]}', 'error')
                    return redirect(url_for('comms_per_user_form'))
                
                # Update Google Sheets (if credentials available)
                sheets_updated = False
                try:
                    credentials_json = os.environ.get('GOOGLE_CREDENTIALS_JSON')
                    if credentials_json or os.path.exists('google_credentials.json'):
                        update_comms_google_sheets(result)
                        sheets_updated = True
                except Exception as e:
                    print(f"Warning: Could not update Google Sheets: {str(e)}")
                    flash(f'Warning: Could not update Google Sheets: {str(e)}', 'warning')
                
                return render_template('comms_per_user_results.html', 
                                     results=result,
                                     sheets_updated=sheets_updated,
                                     sheet_url=f"https://docs.google.com/spreadsheets/d/{GOOGLE_SHEET_ID}")
                
            except ValueError as e:
                flash('Please enter valid numbers for all user counts', 'error')
                return redirect(url_for('comms_per_user_form'))
        
        else:
            # Step 1: Create segments
            result = comms_automation.calculate_comms_per_user(end_date)
            
            if 'error' in result:
                flash(f'Error: {result["error"]}', 'error')
                return redirect(url_for('comms_per_user_form'))
            
            if result.get('step') == 'segments_created':
                # Show segments and ask for manual counts
                return render_template('comms_segments_created.html', 
                                     segments=result['segments'],
                                     end_date=end_date)
            
            # This shouldn't happen with the new flow, but keep as fallback
            flash('Unexpected result from calculation', 'error')
            return redirect(url_for('comms_per_user_form'))
        
    except Exception as e:
        flash(f'Error calculating Communications Per User: {str(e)}', 'error')
        return redirect(url_for('comms_per_user_form'))

@app.route('/calculate-mtu')
def calculate_mtu_form():
    """Show MTU calculation form"""
    return render_template('calculate_mtu.html')

@app.route('/calculate-mtu', methods=['POST'])
def calculate_mtu():
    """Calculate MTU from segment counts"""
    try:
        # Get form data
        segment_counts = {}
        countries = ['UK', 'UAE']
        
        for country in countries:
            segment_counts[f'{country}_all_users'] = int(request.form.get(f'{country.lower()}_all_users', 0))
            segment_counts[f'{country}_active_users'] = int(request.form.get(f'{country.lower()}_active_users', 0))
            segment_counts[f'{country}_push_received'] = int(request.form.get(f'{country.lower()}_push_received', 0))
            segment_counts[f'{country}_push_received_active'] = int(request.form.get(f'{country.lower()}_push_received_active', 0))
            segment_counts[f'{country}_email_received'] = int(request.form.get(f'{country.lower()}_email_received', 0))
            segment_counts[f'{country}_email_received_active'] = int(request.form.get(f'{country.lower()}_email_received_active', 0))
        
        period_info = request.form.get('period', f"Generated on {datetime.now().strftime('%Y-%m-%d')}")
        
        # Calculate MTU percentages
        results = calculate_mtu_percentages(segment_counts)
        
        # Update Google Sheets (if credentials available)
        sheets_updated = False
        try:
            credentials_json = os.environ.get('GOOGLE_CREDENTIALS_JSON')
            if credentials_json or os.path.exists('google_credentials.json'):
                update_google_sheets(results, period_info)
                sheets_updated = True
        except Exception as e:
            print(f"Warning: Could not update Google Sheets: {str(e)}")
            flash(f'Warning: Could not update Google Sheets: {str(e)}', 'warning')
        
        return render_template('mtu_results.html', 
                             results=results,
                             period=period_info,
                             sheets_updated=sheets_updated,
                             sheet_url=f"https://docs.google.com/spreadsheets/d/{GOOGLE_SHEET_ID}")
        
    except Exception as e:
        flash(f'Error calculating MTU: {str(e)}', 'error')
        return redirect(url_for('calculate_mtu_form'))

def calculate_mtu_percentages(segment_counts):
    """Calculate MTU percentages from segment counts"""
    results = {}
    countries = ['UK', 'UAE']
    channels = ['push', 'email']
    
    for country in countries:
        results[country] = {}
        
        # Get base counts
        all_users = segment_counts.get(f"{country}_all_users", 0)
        active_users = segment_counts.get(f"{country}_active_users", 0)
        
        results[country]['all_users'] = all_users
        results[country]['active_users'] = active_users
        
        # Calculate active user percentage
        if all_users > 0:
            active_percentage = (active_users / all_users) * 100
            results[country]['active_percentage'] = round(active_percentage, 2)
        else:
            results[country]['active_percentage'] = 0
        
        # Calculate MTU for each channel
        for channel in channels:
            received = segment_counts.get(f"{country}_{channel}_received", 0)
            received_active = segment_counts.get(f"{country}_{channel}_received_active", 0)
            
            results[country][f'{channel}_received'] = received
            results[country][f'{channel}_received_active'] = received_active
            
            # MTU = (Active users who received comms / Active users) * 100
            if active_users > 0:
                mtu_percentage = (received_active / active_users) * 100
                results[country][f'{channel}_mtu'] = round(mtu_percentage, 2)
            else:
                results[country][f'{channel}_mtu'] = 0
            
            # Additional metric: Reach percentage (received / all users)
            if all_users > 0:
                reach_percentage = (received / all_users) * 100
                results[country][f'{channel}_reach'] = round(reach_percentage, 2)
            else:
                results[country][f'{channel}_reach'] = 0
    
    return results

def update_comms_google_sheets(results):
    """Update Google Sheets with Communications Per User results"""
    # Define the scope
    scope = [
        'https://spreadsheets.google.com/feeds',
        'https://www.googleapis.com/auth/drive'
    ]
    
    # Load credentials from environment variable or file
    credentials_json = os.environ.get('GOOGLE_CREDENTIALS_JSON')
    if credentials_json:
        # Production: Load from environment variable
        credentials_info = json.loads(credentials_json)
        creds = Credentials.from_service_account_info(credentials_info, scopes=scope)
    elif os.path.exists('google_credentials.json'):
        # Development: Load from file
        creds = Credentials.from_service_account_file('google_credentials.json', scopes=scope)
    else:
        raise Exception("No Google credentials found. Please set GOOGLE_CREDENTIALS_JSON environment variable or add google_credentials.json file.")
    
    # Authorize the client
    gc = gspread.authorize(creds)
    
    # Open the specific sheet
    sheet = gc.open_by_key(GOOGLE_SHEET_ID)
    
    # Get or create Communications Per User worksheet
    try:
        worksheet = sheet.worksheet("Communications Per User")
    except gspread.WorksheetNotFound:
        worksheet = sheet.add_worksheet(title="Communications Per User", rows=50, cols=15)
    
    # Clear existing content
    worksheet.clear()
    
    # Prepare data in vertical format
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    data = [
        ['Communications Per User Report', ''],
        ['Generated', timestamp],
        ['Period', results['period']],
        ['', ''],  # Empty row
        ['Metric', 'UK', 'UAE'],
        ['', '', ''],  # Empty row
        ['TRANSACTIONAL COMMUNICATIONS', '', ''],
        ['Transactional PN per User', results['uk']['transactional_pn'], results['uae']['transactional_pn']],
        ['Transactional Email per User', results['uk']['transactional_email'], results['uae']['transactional_email']],
        ['', '', ''],  # Empty row
        ['PROMOTIONAL COMMUNICATIONS', '', ''],
        ['Promotional PN per User', results['uk']['promotional_pn'], results['uae']['promotional_pn']],
        ['Promotional Email per User', results['uk']['promotional_email'], results['uae']['promotional_email']],
        ['', '', ''],  # Empty row
        ['USER COUNTS', '', ''],
        ['Total Users', results['uk']['total_users'], results['uae']['total_users']],
        ['Transacted Users', results['uk']['transacted_users'], results['uae']['transacted_users']],
        ['', '', ''],  # Empty row
        ['RAW COMMUNICATION COUNTS', '', ''],
        ['Transactional PN Sent', results['uk']['raw_counts']['transactional_pn'], results['uae']['raw_counts']['transactional_pn']],
        ['Transactional Email Sent', results['uk']['raw_counts']['transactional_email'], results['uae']['raw_counts']['transactional_email']],
        ['Promotional PN Sent', results['uk']['raw_counts']['promotional_pn'], results['uae']['raw_counts']['promotional_pn']],
        ['Promotional Email Sent', results['uk']['raw_counts']['promotional_email'], results['uae']['raw_counts']['promotional_email']],
    ]
    
    # Update the worksheet
    worksheet.update('A1', data)

def update_google_sheets(results, period_info):
    """Update Google Sheets with MTU results"""
    # Define the scope
    scope = [
        'https://spreadsheets.google.com/feeds',
        'https://www.googleapis.com/auth/drive'
    ]
    
    # Load credentials from environment variable or file
    credentials_json = os.environ.get('GOOGLE_CREDENTIALS_JSON')
    if credentials_json:
        # Production: Load from environment variable
        credentials_info = json.loads(credentials_json)
        creds = Credentials.from_service_account_info(credentials_info, scopes=scope)
    elif os.path.exists('google_credentials.json'):
        # Development: Load from file
        creds = Credentials.from_service_account_file('google_credentials.json', scopes=scope)
    else:
        raise Exception("No Google credentials found. Please set GOOGLE_CREDENTIALS_JSON environment variable or add google_credentials.json file.")
    
    # Authorize the client
    gc = gspread.authorize(creds)
    
    # Open the specific sheet
    sheet = gc.open_by_key(GOOGLE_SHEET_ID)
    
    # Get or create MTU Metrics worksheet
    try:
        worksheet = sheet.worksheet("MTU Metrics")
    except gspread.WorksheetNotFound:
        worksheet = sheet.add_worksheet(title="MTU Metrics", rows=50, cols=10)
    
    # Clear existing content
    worksheet.clear()
    
    # Prepare data in vertical format
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    data = [
        ['MTU Metrics Report', ''],
        ['Generated', timestamp],
        ['Period', period_info],
        ['', ''],  # Empty row
        ['Metric', 'UK', 'UAE'],
        ['', '', ''],  # Empty row
    ]
    
    # Add metrics
    metrics = [
        ('All Users', 'all_users'),
        ('Active Users (60d)', 'active_users'),
        ('Active %', 'active_percentage'),
        ('', ''),  # Empty row
        ('Push Received', 'push_received'),
        ('Push Received (Active)', 'push_received_active'),
        ('Push MTU %', 'push_mtu'),
        ('Push Reach %', 'push_reach'),
        ('', ''),  # Empty row
        ('Email Received', 'email_received'),
        ('Email Received (Active)', 'email_received_active'),
        ('Email MTU %', 'email_mtu'),
        ('Email Reach %', 'email_reach'),
    ]
    
    for label, key in metrics:
        if label == '':
            data.append(['', '', ''])
        else:
            uk_value = results['UK'].get(key, 0)
            uae_value = results['UAE'].get(key, 0)
            
            # Format percentages
            if key.endswith('_percentage') or key.endswith('_mtu') or key.endswith('_reach'):
                uk_value = f"{uk_value}%" if uk_value else "0%"
                uae_value = f"{uae_value}%" if uae_value else "0%"
            
            data.append([label, uk_value, uae_value])
    
    # Update the worksheet
    worksheet.update('A1', data)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)