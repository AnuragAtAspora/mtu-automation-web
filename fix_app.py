#!/usr/bin/env python3
"""
Script to fix the corrupted create_metrics_segments function in app.py
"""

# Read the fixed function
with open('fixed_function.py', 'r') as f:
    fixed_function = f.read()

# Read the current app.py
with open('app.py', 'r') as f:
    lines = f.readlines()

# Find the start and end of the broken function
start_line = None
end_line = None

for i, line in enumerate(lines):
    if line.strip() == 'def create_metrics_segments(start_date, end_date):':
        start_line = i
    elif start_line is not None and line.strip() == 'def calculate_comprehensive_metrics(campaign_data, user_counts):':
        end_line = i
        break

if start_line is not None and end_line is not None:
    print(f"Found broken function from line {start_line + 1} to {end_line}")
    
    # Replace the broken function with the fixed one
    new_lines = lines[:start_line] + [fixed_function + '\n\n'] + lines[end_line:]
    
    # Write the fixed app.py
    with open('app.py', 'w') as f:
        f.writelines(new_lines)
    
    print("✅ Fixed the create_metrics_segments function!")
else:
    print("❌ Could not find the function boundaries")