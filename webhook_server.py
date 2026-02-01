#!/usr/bin/env python3
"""
MoEngage Data Export Webhook Server
Receives real-time event data from MoEngage Streams
"""

from flask import Flask, request, jsonify
import json
import sqlite3
from datetime import datetime, timedelta
import threading
import time
import os

app = Flask(__name__)

class MoEngageDataProcessor:
    def __init__(self, db_path="moengage_data.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize SQLite database for storing MoEngage events"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Events table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                event_uuid TEXT UNIQUE,
                event_name TEXT,
                event_code TEXT,
                event_time INTEGER,
                event_type TEXT,
                event_source TEXT,
                uid TEXT,
                push_id TEXT,
                email_id TEXT,
                mobile_number TEXT,
                campaign_id TEXT,
                campaign_name TEXT,
                campaign_type TEXT,
                campaign_channel TEXT,
                user_attributes TEXT,
                device_attributes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # User metrics table for quick lookups
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_metrics (
                date TEXT PRIMARY KEY,
                total_users INTEGER,
                active_users INTEGER,
                email_users INTEGER,
                push_users INTEGER,
                campaign_interactions INTEGER,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
        print("✅ Database initialized")
    
    def process_events(self, events_data):
        """Process incoming events from MoEngage"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            app_name = events_data.get('app_name', '')
            moe_request_id = events_data.get('moe_request_id', '')
            events = events_data.get('events', [])
            
            processed_count = 0
            
            for event in events:
                try:
                    # Extract event data
                    event_uuid = event.get('event_uuid', '')
                    event_name = event.get('event_name', '')
                    event_code = event.get('event_code', '')
                    event_time = event.get('event_time', 0)
                    event_type = event.get('event_type', '')
                    event_source = event.get('event_source', '')
                    uid = event.get('uid', '')
                    push_id = event.get('push_id', '')
                    email_id = event.get('email_id', '')
                    mobile_number = event.get('mobile_number', '')
                    
                    # Extract campaign attributes
                    event_attrs = event.get('event_attributes', {})
                    campaign_id = event_attrs.get('campaign_id', '')
                    campaign_name = event_attrs.get('campaign_name', '')
                    campaign_type = event_attrs.get('campaign_type', '')
                    campaign_channel = event_attrs.get('campaign_channel', '')
                    
                    # Store user and device attributes as JSON
                    user_attributes = json.dumps(event.get('user_attributes', {}))
                    device_attributes = json.dumps(event.get('device_attributes', {}))
                    
                    # Insert event (ignore duplicates)
                    cursor.execute('''
                        INSERT OR IGNORE INTO events (
                            event_uuid, event_name, event_code, event_time, event_type,
                            event_source, uid, push_id, email_id, mobile_number,
                            campaign_id, campaign_name, campaign_type, campaign_channel,
                            user_attributes, device_attributes
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        event_uuid, event_name, event_code, event_time, event_type,
                        event_source, uid, push_id, email_id, mobile_number,
                        campaign_id, campaign_name, campaign_type, campaign_channel,
                        user_attributes, device_attributes
                    ))
                    
                    if cursor.rowcount > 0:
                        processed_count += 1
                        
                except Exception as e:
                    print(f"⚠️  Error processing event: {e}")
                    continue
            
            conn.commit()
            conn.close()
            
            # Update daily metrics
            self.update_daily_metrics()
            
            print(f"✅ Processed {processed_count} new events from {len(events)} total")
            return processed_count
            
        except Exception as e:
            print(f"❌ Error processing events: {e}")
            return 0
    
    def update_daily_metrics(self):
        """Update daily user metrics from events"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            today = datetime.now().strftime('%Y-%m-%d')
            
            # Calculate metrics for today
            cursor.execute('''
                SELECT 
                    COUNT(DISTINCT uid) as total_users,
                    COUNT(DISTINCT CASE WHEN event_time >= ? THEN uid END) as active_users,
                    COUNT(DISTINCT CASE WHEN email_id != '' THEN uid END) as email_users,
                    COUNT(DISTINCT CASE WHEN push_id != '' THEN uid END) as push_users,
                    COUNT(*) as campaign_interactions
                FROM events 
                WHERE date(datetime(event_time, 'unixepoch')) = ?
            ''', (int(time.time()) - 86400, today))  # Last 24 hours for active users
            
            result = cursor.fetchone()
            if result:
                total_users, active_users, email_users, push_users, interactions = result
                
                # Update or insert metrics
                cursor.execute('''
                    INSERT OR REPLACE INTO user_metrics 
                    (date, total_users, active_users, email_users, push_users, campaign_interactions)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (today, total_users, active_users, email_users, push_users, interactions))
                
                conn.commit()
            
            conn.close()
            
        except Exception as e:
            print(f"⚠️  Error updating metrics: {e}")
    
    def get_user_count(self, date=None):
        """Get user count for a specific date"""
        if not date:
            date = datetime.now().strftime('%Y-%m-%d')
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT total_users, active_users, email_users, push_users 
                FROM user_metrics 
                WHERE date = ?
            ''', (date,))
            
            result = cursor.fetchone()
            conn.close()
            
            if result:
                return {
                    'total_users': result[0],
                    'active_users': result[1], 
                    'email_users': result[2],
                    'push_users': result[3],
                    'date': date
                }
            else:
                return None
                
        except Exception as e:
            print(f"❌ Error getting user count: {e}")
            return None
    
    def get_date_range_metrics(self, start_date, end_date):
        """Get aggregated metrics for a date range"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT 
                    MAX(total_users) as max_users,
                    AVG(active_users) as avg_active_users,
                    SUM(campaign_interactions) as total_interactions
                FROM user_metrics 
                WHERE date BETWEEN ? AND ?
            ''', (start_date, end_date))
            
            result = cursor.fetchone()
            conn.close()
            
            if result and result[0]:
                return {
                    'max_users': result[0],
                    'avg_active_users': int(result[1]) if result[1] else 0,
                    'total_interactions': result[2] if result[2] else 0,
                    'start_date': start_date,
                    'end_date': end_date
                }
            else:
                return None
                
        except Exception as e:
            print(f"❌ Error getting date range metrics: {e}")
            return None

# Initialize data processor
data_processor = MoEngageDataProcessor()

@app.route('/moengage/webhook', methods=['POST'])
def moengage_webhook():
    """Webhook endpoint for MoEngage Data Export"""
    try:
        # Get JSON data
        events_data = request.get_json()
        
        if not events_data:
            return jsonify({'error': 'No data received'}), 400
        
        # Log incoming request
        app_name = events_data.get('app_name', 'Unknown')
        event_count = len(events_data.get('events', []))
        print(f"📥 Received {event_count} events from {app_name}")
        
        # Process events
        processed = data_processor.process_events(events_data)
        
        return jsonify({
            'status': 'success',
            'processed_events': processed,
            'total_events': event_count,
            'message': f'Successfully processed {processed} events'
        }), 200
        
    except Exception as e:
        print(f"❌ Webhook error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/metrics/users/<date>', methods=['GET'])
def get_user_metrics(date):
    """API endpoint to get user metrics for a specific date"""
    try:
        metrics = data_processor.get_user_count(date)
        if metrics:
            return jsonify(metrics), 200
        else:
            return jsonify({'error': 'No data found for date'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/metrics/range', methods=['GET'])
def get_range_metrics():
    """API endpoint to get metrics for a date range"""
    try:
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        if not start_date or not end_date:
            return jsonify({'error': 'start_date and end_date required'}), 400
        
        metrics = data_processor.get_date_range_metrics(start_date, end_date)
        if metrics:
            return jsonify(metrics), 200
        else:
            return jsonify({'error': 'No data found for date range'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'database': os.path.exists(data_processor.db_path)
    }), 200

if __name__ == '__main__':
    print("🚀 Starting MoEngage Data Export Webhook Server")
    print("=" * 50)
    print("📡 Webhook endpoint: http://localhost:5000/moengage/webhook")
    print("📊 User metrics API: http://localhost:5000/metrics/users/<date>")
    print("📈 Range metrics API: http://localhost:5000/metrics/range?start_date=X&end_date=Y")
    print("💚 Health check: http://localhost:5000/health")
    print("=" * 50)
    
    app.run(host='0.0.0.0', port=5000, debug=True)