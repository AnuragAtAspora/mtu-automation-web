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

# Initialize automation
automation = MTUWebAutomation()

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