"""
MoEngage Metrics Web Application
Clean, modular implementation
"""
from flask import Flask, render_template, request, redirect, url_for, flash, session, send_file
from datetime import datetime, timedelta
import json
import os
import csv
import io
import pickle
import tempfile

# Import our modules
from modules import SegmentCreator, CampaignFetcher, MetricsCalculator
import config

app = Flask(__name__)
app.secret_key = config.SECRET_KEY
app.permanent_session_lifetime = timedelta(hours=2)  # Session lasts 2 hours

# Use temp directory for cache storage (persists across requests)
CACHE_DIR = os.path.join(tempfile.gettempdir(), 'moengage_cache')
os.makedirs(CACHE_DIR, exist_ok=True)

def save_to_cache(session_id, data):
    """Save data to file-based cache"""
    cache_file = os.path.join(CACHE_DIR, f"{session_id}.pkl")
    with open(cache_file, 'wb') as f:
        pickle.dump(data, f)

def load_from_cache(session_id):
    """Load data from file-based cache"""
    cache_file = os.path.join(CACHE_DIR, f"{session_id}.pkl")
    if not os.path.exists(cache_file):
        return None
    with open(cache_file, 'rb') as f:
        return pickle.load(f)

# Make datetime available in templates
@app.context_processor
def inject_datetime():
    return {'datetime': datetime}


# ============================================================================
# ROUTES
# ============================================================================

@app.route('/')
def index():
    """Step 1: Date selection"""
    return render_template('index.html')


@app.route('/settings')
def settings():
    """Settings page for managing transactional campaigns"""
    try:
        # Load transactional campaigns from JSON file
        if os.path.exists('transactional_campaigns.json'):
            with open('transactional_campaigns.json', 'r') as f:
                campaigns = json.load(f)
        else:
            campaigns = []
        
        return render_template('settings.html', campaigns=campaigns)
    except Exception as e:
        print(f"Error loading settings: {e}")
        flash('Error loading settings', 'error')
        return render_template('settings.html', campaigns=[])


@app.route('/add-transactional-campaign', methods=['POST'])
def add_transactional_campaign():
    """Add a new transactional campaign"""
    try:
        campaign_id = request.form.get('campaign_id', '').strip()
        campaign_name = request.form.get('campaign_name', '').strip()
        country = request.form.get('country', '').strip()
        
        if not campaign_id or not campaign_name or not country:
            flash('All fields are required', 'error')
            return redirect(url_for('settings'))
        
        # Load existing campaigns
        if os.path.exists('transactional_campaigns.json'):
            with open('transactional_campaigns.json', 'r') as f:
                campaigns = json.load(f)
        else:
            campaigns = []
        
        # Check if campaign already exists
        if any(c['campaign_id'] == campaign_id for c in campaigns):
            flash('Campaign ID already exists', 'error')
            return redirect(url_for('settings'))
        
        # Add new campaign
        campaigns.append({
            'campaign_id': campaign_id,
            'campaign_name': campaign_name,
            'country': country
        })
        
        # Save to file
        with open('transactional_campaigns.json', 'w') as f:
            json.dump(campaigns, f, indent=2)
        
        flash(f'Campaign "{campaign_name}" added successfully', 'success')
        return redirect(url_for('settings'))
        
    except Exception as e:
        print(f"Error adding campaign: {e}")
        flash(f'Error adding campaign: {str(e)}', 'error')
        return redirect(url_for('settings'))


@app.route('/delete-transactional-campaign', methods=['POST'])
def delete_transactional_campaign():
    """Delete a transactional campaign"""
    try:
        campaign_id = request.form.get('campaign_id', '').strip()
        
        if not campaign_id:
            flash('Campaign ID is required', 'error')
            return redirect(url_for('settings'))
        
        # Load existing campaigns
        if os.path.exists('transactional_campaigns.json'):
            with open('transactional_campaigns.json', 'r') as f:
                campaigns = json.load(f)
        else:
            campaigns = []
        
        # Remove campaign
        campaigns = [c for c in campaigns if c['campaign_id'] != campaign_id]
        
        # Save to file
        with open('transactional_campaigns.json', 'w') as f:
            json.dump(campaigns, f, indent=2)
        
        flash('Campaign deleted successfully', 'success')
        return redirect(url_for('settings'))
        
    except Exception as e:
        print(f"Error deleting campaign: {e}")
        flash(f'Error deleting campaign: {str(e)}', 'error')
        return redirect(url_for('settings'))


@app.route('/health')
def health():
    """Health check endpoint"""
    return {"status": "ok", "message": "MoEngage Metrics App is running"}, 200


@app.route('/create-segments', methods=['POST'])
def create_segments():
    """
    Step 2: Create segments in MoEngage
    - Takes date range from form
    - Creates 16 segments using Segmentation API
    - Shows segment links for user to get counts
    """
    try:
        # Make session permanent (lasts 2 hours)
        session.permanent = True
        
        start_date = request.form.get('start_date')
        end_date = request.form.get('end_date')
        
        if not start_date or not end_date:
            flash('Please select both start and end dates', 'error')
            return redirect(url_for('index'))
        
        # Validate dates
        try:
            start_dt = datetime.strptime(start_date, '%Y-%m-%d')
            end_dt = datetime.strptime(end_date, '%Y-%m-%d')
            
            if start_dt > end_dt:
                flash('Start date must be before end date', 'error')
                return redirect(url_for('index'))
        except ValueError:
            flash('Invalid date format', 'error')
            return redirect(url_for('index'))
        
        # Create segments
        print(f"\n{'='*60}")
        print(f"CREATING SEGMENTS FOR {start_date} to {end_date}")
        print(f"{'='*60}\n")
        
        segment_creator = SegmentCreator(
            workspace_id=config.MOENGAGE_CONFIG['workspace_id'],
            data_api_key=config.MOENGAGE_CONFIG['data_api_key'],
            data_center=config.MOENGAGE_CONFIG['data_center']
        )
        
        result = segment_creator.create_metrics_segments(
            start_date,
            end_date,
            rate_limit_delay=config.RATE_LIMIT_DELAY
        )
        
        if not result['success']:
            flash(f"Some segments failed to create. Check logs for details.", 'warning')
        
        # Store segment IDs in session for later cleanup if needed
        session['segment_ids'] = result['segment_ids']
        session['start_date'] = start_date
        session['end_date'] = end_date
        
        print(f"\n{'='*60}")
        print(f"SEGMENTS CREATED: {result['total_created']}/{result['total_created'] + result['total_failed']}")
        print(f"{'='*60}\n")
        
        return render_template('segments_created.html',
                             start_date=start_date,
                             end_date=end_date,
                             segments=result['segments'],
                             failed=result['failed'])
        
    except Exception as e:
        print(f"Error creating segments: {e}")
        import traceback
        traceback.print_exc()
        flash(f'Error creating segments: {str(e)}', 'error')
        return redirect(url_for('index'))


@app.route('/calculate-metrics', methods=['POST'])
def calculate_metrics():
    """
    Step 3: Calculate metrics
    - Takes segment counts from form
    - Fetches campaign data using Stats API + Campaign Meta API
    - Calculates all metrics
    - Shows results
    """
    try:
        # Make session permanent (lasts 2 hours)
        session.permanent = True
        
        # Get dates from session
        start_date = session.get('start_date')
        end_date = session.get('end_date')
        
        if not start_date or not end_date:
            flash('Session expired. Please start over.', 'error')
            return redirect(url_for('index'))
        
        # Get segment counts from form
        user_counts = {
            'uk_total_users': int(request.form.get('uk_total_users', 0)),
            'uk_active_users': int(request.form.get('uk_active_users', 0)),
            'uk_push_received': int(request.form.get('uk_push_received', 0)),
            'uk_email_received': int(request.form.get('uk_email_received', 0)),
            'uk_push_received_active': int(request.form.get('uk_push_received_active', 0)),
            'uk_email_received_active': int(request.form.get('uk_email_received_active', 0)),
            'uk_push_unsubscribed': int(request.form.get('uk_push_unsubscribed', 0)),
            'uk_email_unsubscribed': int(request.form.get('uk_email_unsubscribed', 0)),
            'uae_total_users': int(request.form.get('uae_total_users', 0)),
            'uae_active_users': int(request.form.get('uae_active_users', 0)),
            'uae_push_received': int(request.form.get('uae_push_received', 0)),
            'uae_email_received': int(request.form.get('uae_email_received', 0)),
            'uae_push_received_active': int(request.form.get('uae_push_received_active', 0)),
            'uae_email_received_active': int(request.form.get('uae_email_received_active', 0)),
            'uae_push_unsubscribed': int(request.form.get('uae_push_unsubscribed', 0)),
            'uae_email_unsubscribed': int(request.form.get('uae_email_unsubscribed', 0)),
        }
        
        print(f"\n{'='*60}")
        print(f"FETCHING CAMPAIGN DATA FOR {start_date} to {end_date}")
        print(f"{'='*60}\n")
        
        # Fetch campaign data
        campaign_fetcher = CampaignFetcher(
            workspace_id=config.MOENGAGE_CONFIG['workspace_id'],
            campaign_api_key=config.MOENGAGE_CONFIG['campaign_api_key'],
            data_center=config.MOENGAGE_CONFIG['data_center']
        )
        
        campaigns = campaign_fetcher.fetch_all_campaigns(
            start_date,
            end_date,
            max_pages=config.MAX_CAMPAIGN_PAGES,
            fetch_meta=True
        )
        
        print(f"Fetched {len(campaigns)} campaigns")
        
        if not campaigns:
            print("ERROR: No campaigns returned from API")
            flash('No campaigns found for the selected period. Please check the date range or try again later.', 'warning')
            return redirect(url_for('index'))
        
        # Check if we hit the limit
        if len(campaigns) >= (config.MAX_CAMPAIGN_PAGES * 15):
            flash(f'Warning: Fetched {len(campaigns)} campaigns (limit reached). There may be more campaigns in this period. Consider using a shorter date range for complete data.', 'warning')
        
        # Group campaigns by category
        categories = campaign_fetcher.group_campaigns_by_category(campaigns)
        
        # Aggregate metrics for each category
        aggregated_metrics = {}
        for category_name, campaign_list in categories.items():
            aggregated_metrics[category_name] = campaign_fetcher.aggregate_campaign_metrics(campaign_list)
        
        # Prepare campaign data for metrics calculation
        campaign_data = MetricsCalculator.prepare_campaign_data_for_calculation(
            categories,
            aggregated_metrics
        )
        
        print(f"\n{'='*60}")
        print(f"CALCULATING METRICS")
        print(f"{'='*60}\n")
        
        # Calculate metrics
        metrics = MetricsCalculator.calculate_metrics(campaign_data, user_counts)
        
        # Generate unique session ID
        import uuid
        session_id = str(uuid.uuid4())
        
        # Store data in file-based cache instead of memory
        cache_data = {
            'campaign_data': campaign_data,
            'user_counts': user_counts,
            'metrics': metrics,
            'categories': {k: [{'campaign_id': c['campaign_id'], 
                              'campaign_name': c.get('campaign_name', ''),
                              'campaign_start_time': c.get('campaign_start_time', ''),
                              'sent': c.get('sent', 0),
                              'delivered': c.get('delivered', 0),
                              'click': c.get('click', 0)} 
                             for c in v] 
                            for k, v in categories.items()},
            'start_date': start_date,
            'end_date': end_date
        }
        
        save_to_cache(session_id, cache_data)
        
        # Store only session ID in session
        session['session_id'] = session_id
        
        print(f"\n{'='*60}")
        print(f"METRICS CALCULATED SUCCESSFULLY")
        print(f"{'='*60}\n")
        
        return render_template('results.html',
                             start_date=start_date,
                             end_date=end_date,
                             metrics=metrics,
                             campaign_data=campaign_data,
                             user_counts=user_counts,
                             total_campaigns=len(campaigns),
                             categories=categories)
        
    except Exception as e:
        print(f"Error calculating metrics: {e}")
        import traceback
        traceback.print_exc()
        flash(f'Error calculating metrics: {str(e)}', 'error')
        return redirect(url_for('index'))


@app.route('/download-csv/<category>')
def download_csv(category):
    """
    Download campaign data as CSV for a specific category
    Categories: uk_promotional_push, uk_promotional_email, uk_transactional_push, uk_transactional_email,
                uae_promotional_push, uae_promotional_email, uae_transactional_push, uae_transactional_email
    """
    try:
        # Get session ID
        session_id = session.get('session_id')
        
        if not session_id:
            flash('Session expired. Please calculate metrics again.', 'error')
            return redirect(url_for('index'))
        
        # Get data from cache
        cached_data = load_from_cache(session_id)
        
        if not cached_data:
            flash('Session expired. Please calculate metrics again.', 'error')
            return redirect(url_for('index'))
        
        categories = cached_data['categories']
        start_date = cached_data['start_date']
        end_date = cached_data['end_date']
        
        if category not in categories:
            flash('Invalid category', 'error')
            return redirect(url_for('index'))
        
        campaigns = categories[category]
        
        # Create CSV in memory
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write header
        writer.writerow(['Campaign Name', 'Sent Day', 'Nature', 'Total Sent', 'Total Clicks'])
        
        # Determine nature from category
        if 'promotional' in category:
            nature = 'Promotional'
        elif 'transactional' in category:
            nature = 'Transactional'
        else:
            nature = 'Unknown'
        
        # Write campaign data
        for campaign in campaigns:
            campaign_name = campaign.get('campaign_name', 'N/A')
            sent = campaign.get('sent', 0)
            clicks = campaign.get('click', 0)
            
            # Sent day - use campaign_start_time if available, otherwise use start_date
            campaign_start_time = campaign.get('campaign_start_time', '')
            if campaign_start_time:
                # Extract just the date part (YYYY-MM-DD) from datetime string
                sent_day = campaign_start_time.split('T')[0] if 'T' in campaign_start_time else campaign_start_time[:10]
            else:
                sent_day = start_date
            
            writer.writerow([campaign_name, sent_day, nature, sent, clicks])
        
        # Prepare file for download
        output.seek(0)
        
        # Create filename
        category_name = category.replace('_', '-')
        filename = f"{category_name}_{start_date}_to_{end_date}.csv"
        
        # Convert StringIO to BytesIO for send_file
        mem = io.BytesIO()
        mem.write(output.getvalue().encode('utf-8'))
        mem.seek(0)
        
        return send_file(
            mem,
            mimetype='text/csv',
            as_attachment=True,
            download_name=filename
        )
        
    except Exception as e:
        print(f"Error generating CSV: {e}")
        import traceback
        traceback.print_exc()
        flash(f'Error generating CSV: {str(e)}', 'error')
        return redirect(url_for('index'))


# ============================================================================
# RUN APP
# ============================================================================

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=config.DEBUG)
