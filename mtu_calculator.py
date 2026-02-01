#!/usr/bin/env python3
"""
MTU Calculator with Google Sheets Integration
Calculates MTU percentages from manual segment counts and updates Google Sheets
"""

import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
import json

class MTUCalculator:
    def __init__(self, credentials_file="google_credentials.json"):
        """Initialize with Google Sheets credentials"""
        self.credentials_file = credentials_file
        self.gc = None
        self.sheet = None
        self.worksheet = None
        self.setup_google_sheets()
    
    def setup_google_sheets(self):
        """Setup Google Sheets connection"""
        try:
            # Define the scope
            scope = [
                'https://spreadsheets.google.com/feeds',
                'https://www.googleapis.com/auth/drive'
            ]
            
            # Load credentials
            creds = Credentials.from_service_account_file(
                self.credentials_file, 
                scopes=scope
            )
            
            # Authorize the client
            self.gc = gspread.authorize(creds)
            
            # Open the specific sheet
            sheet_id = "1A30FfO319eiKW0c6zHj2lwr04WLE0fL6eLteZf4CvHM"
            self.sheet = self.gc.open_by_key(sheet_id)
            
            # Get or create MTU Metrics worksheet
            try:
                self.worksheet = self.sheet.worksheet("MTU Metrics")
                print("✅ Connected to existing 'MTU Metrics' worksheet")
            except gspread.WorksheetNotFound:
                self.worksheet = self.sheet.add_worksheet(title="MTU Metrics", rows=50, cols=10)
                print("✅ Created new 'MTU Metrics' worksheet")
                
        except Exception as e:
            print(f"❌ Error setting up Google Sheets: {e}")
            raise
    
    def get_segment_counts_input(self):
        """Get segment counts from user input"""
        print("\n📊 MTU Segment Count Input")
        print("=" * 40)
        print("Enter the user counts for each segment from MoEngage dashboard:")
        print("(Enter 0 if segment doesn't exist or has no users)")
        
        countries = ['UK', 'UAE']
        channels = ['Push', 'Email']
        
        segment_counts = {}
        
        for country in countries:
            print(f"\n--- {country} Segments ---")
            
            # All users in country
            while True:
                try:
                    count = int(input(f"{country} - All Users: "))
                    segment_counts[f"{country}_all_users"] = count
                    break
                except ValueError:
                    print("Please enter a valid number")
            
            # Active users (60 days)
            while True:
                try:
                    count = int(input(f"{country} - Active Users (60 days): "))
                    segment_counts[f"{country}_active_users"] = count
                    break
                except ValueError:
                    print("Please enter a valid number")
            
            # Communication segments
            for channel in channels:
                # Users who received communications
                while True:
                    try:
                        count = int(input(f"{country} - {channel} Received: "))
                        segment_counts[f"{country}_{channel.lower()}_received"] = count
                        break
                    except ValueError:
                        print("Please enter a valid number")
                
                # Active users who received communications
                while True:
                    try:
                        count = int(input(f"{country} - {channel} Received (Active): "))
                        segment_counts[f"{country}_{channel.lower()}_received_active"] = count
                        break
                    except ValueError:
                        print("Please enter a valid number")
        
        return segment_counts
    
    def calculate_mtu_percentages(self, segment_counts):
        """Calculate MTU percentages from segment counts"""
        print("\n🧮 Calculating MTU Percentages...")
        
        results = {}
        countries = ['UK', 'UAE']
        channels = ['push', 'email']
        
        for country in countries:
            country_key = country.lower()
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
    
    def update_google_sheets(self, results, period_info):
        """Update Google Sheets with MTU results"""
        print("\n📝 Updating Google Sheets...")
        
        try:
            # Clear existing content
            self.worksheet.clear()
            
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
            self.worksheet.update('A1', data)
            
            # Format the sheet
            self.format_worksheet()
            
            print("✅ Google Sheets updated successfully!")
            print(f"🔗 View at: https://docs.google.com/spreadsheets/d/{self.sheet.id}")
            
        except Exception as e:
            print(f"❌ Error updating Google Sheets: {e}")
    
    def format_worksheet(self):
        """Apply formatting to the worksheet"""
        try:
            # Bold headers
            self.worksheet.format('A1:C1', {'textFormat': {'bold': True}})
            self.worksheet.format('A5:C5', {'textFormat': {'bold': True}})
            
            # Center align data columns
            self.worksheet.format('B:C', {'horizontalAlignment': 'CENTER'})
            
            print("✅ Worksheet formatting applied")
            
        except Exception as e:
            print(f"⚠️  Warning: Could not apply formatting: {e}")
    
    def print_results_summary(self, results):
        """Print a summary of the results"""
        print("\n📊 MTU CALCULATION RESULTS")
        print("=" * 50)
        
        for country in ['UK', 'UAE']:
            print(f"\n--- {country} ---")
            print(f"All Users: {results[country]['all_users']:,}")
            print(f"Active Users: {results[country]['active_users']:,}")
            print(f"Active %: {results[country]['active_percentage']}%")
            print()
            
            for channel in ['push', 'email']:
                print(f"{channel.title()} Received: {results[country][f'{channel}_received']:,}")
                print(f"{channel.title()} Received (Active): {results[country][f'{channel}_received_active']:,}")
                print(f"{channel.title()} MTU: {results[country][f'{channel}_mtu']}%")
                print(f"{channel.title()} Reach: {results[country][f'{channel}_reach']}%")
                print()
    
    def save_results_json(self, results, segment_counts, period_info):
        """Save results to JSON file for record keeping"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"mtu_results_{timestamp}.json"
        
        data = {
            'timestamp': datetime.now().isoformat(),
            'period': period_info,
            'segment_counts': segment_counts,
            'results': results
        }
        
        try:
            with open(filename, 'w') as f:
                json.dump(data, f, indent=2)
            print(f"✅ Results saved to {filename}")
        except Exception as e:
            print(f"⚠️  Warning: Could not save JSON file: {e}")

def main():
    print("🚀 MTU Calculator with Google Sheets Integration")
    print("=" * 50)
    
    # Get period information
    period_info = input("Enter the period for this MTU calculation (e.g., 'January 2026'): ").strip()
    if not period_info:
        period_info = f"Generated on {datetime.now().strftime('%Y-%m-%d')}"
    
    try:
        # Initialize calculator
        calculator = MTUCalculator()
        
        # Get segment counts from user
        segment_counts = calculator.get_segment_counts_input()
        
        # Calculate MTU percentages
        results = calculator.calculate_mtu_percentages(segment_counts)
        
        # Print results summary
        calculator.print_results_summary(results)
        
        # Update Google Sheets
        calculator.update_google_sheets(results, period_info)
        
        # Save results to JSON
        calculator.save_results_json(results, segment_counts, period_info)
        
        print("\n🎉 MTU calculation completed successfully!")
        print("\n📝 NEXT STEPS:")
        print("1. Review the results in Google Sheets")
        print("2. Use MTU percentages for marketing analysis")
        print("3. Compare with previous periods if available")
        
    except KeyboardInterrupt:
        print("\n\n❌ Operation cancelled by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("Please check your setup and try again")

if __name__ == "__main__":
    main()