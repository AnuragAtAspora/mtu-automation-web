#!/usr/bin/env python3
"""
Railway Environment Variable Setup Helper
Generates the GOOGLE_CREDENTIALS_JSON environment variable value for Railway deployment
"""

import json

def setup_railway_env():
    """Generate environment variable value for Railway"""
    
    print("Railway Environment Variable Setup")
    print("=" * 40)
    
    try:
        # Read the Google credentials file
        with open('google_credentials.json', 'r') as f:
            credentials = json.load(f)
        
        # Convert to single-line JSON string (required for environment variables)
        credentials_json = json.dumps(credentials, separators=(',', ':'))
        
        print("✅ Google credentials loaded successfully")
        print("\n📋 COPY THIS VALUE TO RAILWAY:")
        print("-" * 40)
        print(credentials_json)
        print("-" * 40)
        
        print("\n📝 RAILWAY SETUP INSTRUCTIONS:")
        print("1. Go to your Railway project dashboard")
        print("2. Click on 'Variables' tab")
        print("3. Add new variable:")
        print("   - Name: GOOGLE_CREDENTIALS_JSON")
        print("   - Value: [paste the JSON string above]")
        print("4. Click 'Add' to save")
        print("5. Your app will automatically redeploy with the new variable")
        
        print(f"\n🔗 Your app URL: https://web-production-c1afd.up.railway.app/")
        
        # Also save to a file for easy copying
        with open('railway_env_value.txt', 'w') as f:
            f.write(credentials_json)
        
        print(f"\n💾 Environment variable value also saved to: railway_env_value.txt")
        
    except FileNotFoundError:
        print("❌ Error: google_credentials.json file not found")
        print("   Make sure the file exists in the current directory")
    except json.JSONDecodeError:
        print("❌ Error: Invalid JSON in google_credentials.json")
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    setup_railway_env()