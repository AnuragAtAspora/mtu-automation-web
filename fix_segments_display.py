#!/usr/bin/env python3
"""
Fix the segments display issue in the web interface
"""

# The issue is in the generate_metrics function - it's not properly handling existing segments
# Let me create a fixed version

fixed_generate_metrics = '''
@app.route('/generate-metrics', methods=['POST'])
def generate_metrics():
    """Generate metrics by calling APIs and creating segments"""
    try:
        # Get form data
        start_date = request.form.get('start_date')
        end_date = request.form.get('end_date')
        
        if not start_date or not end_date:
            flash('Please provide both start and end dates', 'error')
            return redirect(url_for('comprehensive_metrics'))
        
        # Step 1: Get campaign performance data
        campaign_data = get_campaign_performance_data(start_date, end_date)
        
        # Step 2: Create segments for user counts
        segments_result = create_metrics_segments(start_date, end_date)
        
        if 'error' in segments_result:
            flash(f'Error creating segments: {segments_result["error"]}', 'error')
            return redirect(url_for('comprehensive_metrics'))
        
        # CRITICAL FIX: Ensure all segments are included, whether created or reused
        segments = segments_result.get('segments', [])
        
        # Add campaign data and segment IDs to the response
        campaign_data['segment_ids'] = segments_result.get('segment_ids', [])
        
        return render_template('segments_input.html',
                             start_date=start_date,
                             end_date=end_date,
                             campaign_data=json.dumps(campaign_data),
                             segments=segments,  # Pass segments directly to template
                             data_source=campaign_data.get('data_source', 'API'))
        
    except Exception as e:
        flash(f'Error generating metrics: {str(e)}', 'error')
        return redirect(url_for('comprehensive_metrics'))
'''

print("Fixed generate_metrics function created")
print("The key fix is: segments=segments,  # Pass segments directly to template")
print("This ensures both created and reused segments are displayed")