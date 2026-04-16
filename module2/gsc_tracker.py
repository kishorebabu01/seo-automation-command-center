# ============================================================
# GOOGLE SEARCH CONSOLE API TRACKER
# ============================================================
# This connects to Google Search Console and fetches:
# - Which pages are ranking
# - What keywords bring clicks
# - How many impressions each page gets
# ============================================================

# To use this, you need:
# 1. Google Cloud Console account (free)
# 2. Enable Search Console API
# 3. Download credentials.json
# We'll set that up step by step below

import json
import os
from datetime import datetime, timedelta

# Try to import Google API libraries
# If not installed, we show a helpful message
try:
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from google.auth.transport.requests import Request
    from googleapiclient.discovery import build
    GOOGLE_AVAILABLE = True
except ImportError:
    GOOGLE_AVAILABLE = False
    print("⚠️ Google API libraries not installed")
    print("Run: pip install google-auth google-auth-oauthlib google-api-python-client")


# ---- CONFIGURATION ----
# Scopes = What permissions we're asking from Google
SCOPES = ['https://www.googleapis.com/auth/webmasters.readonly']

# This is the file Google gives you (we'll download it)
CREDENTIALS_FILE = 'credentials.json'

# This file saves your login so you don't log in every time
TOKEN_FILE = 'token.json'


def get_gsc_service():
    """
    Connects to Google Search Console
    Returns a 'service' object we can use to make requests
    
    Authentication flow:
    1. First time: Opens browser for Google login
    2. After that: Uses saved token automatically
    """
    
    if not GOOGLE_AVAILABLE:
        return None
    
    creds = None
    
    # Check if we have a saved token from previous login
    if os.path.exists(TOKEN_FILE):
        # Load saved credentials
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
    
    # If no saved credentials OR they're expired
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            # Try to refresh the token automatically
            creds.refresh(Request())
        else:
            # Need to log in fresh - opens browser
            if not os.path.exists(CREDENTIALS_FILE):
                print("❌ credentials.json not found!")
                print("📋 Follow these steps:")
                print("1. Go to: https://console.cloud.google.com")
                print("2. Create new project")
                print("3. Enable 'Google Search Console API'")
                print("4. Create OAuth 2.0 credentials")
                print("5. Download as 'credentials.json'")
                print("6. Put it in the module2 folder")
                return None
            
            # Start OAuth flow - opens browser for Google login
            flow = InstalledAppFlow.from_client_secrets_file(
                CREDENTIALS_FILE, SCOPES)
            creds = flow.run_local_server(port=0)
        
        # Save credentials for next time
        with open(TOKEN_FILE, 'w') as token:
            token.write(creds.to_json())
    
    # Build and return the service object
    service = build('searchconsole', 'v1', credentials=creds)
    print("✅ Connected to Google Search Console!")
    return service


def get_performance_data(service, site_url, days=30):
    """
    Gets search performance data for your site
    
    Parameters:
    - service: the GSC connection object
    - site_url: your website URL registered in GSC
    - days: how many days of data to fetch
    
    Returns data including:
    - queries (keywords people searched)
    - clicks (how many clicked your result)
    - impressions (how many times shown)
    - position (average rank)
    """
    
    if not service:
        print("⚠️ No GSC connection. Using sample data instead.")
        return get_sample_data()
    
    # Calculate date range
    end_date = datetime.now().strftime('%Y-%m-%d')
    start_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
    
    print(f"📊 Fetching data from {start_date} to {end_date}...")
    
    try:
        # Make API request to Google
        # This is like asking Google: "Show me my website's search data"
        response = service.searchanalytics().query(
            siteUrl=site_url,
            body={
                'startDate': start_date,
                'endDate': end_date,
                'dimensions': ['query', 'page'],  # Group by keyword AND page
                'rowLimit': 1000,  # Get up to 1000 rows
                'startRow': 0
            }
        ).execute()
        
        # Process the response
        rows = response.get('rows', [])
        print(f"✅ Got {len(rows)} rows of data from GSC")
        
        results = []
        for row in rows:
            results.append({
                'query': row['keys'][0],      # The search keyword
                'page': row['keys'][1],        # The page URL
                'clicks': row['clicks'],        # Number of clicks
                'impressions': row['impressions'],  # Times shown in Google
                'ctr': round(row['ctr'] * 100, 2),  # Click rate %
                'position': round(row['position'], 1)  # Average position
            })
        
        return results
        
    except Exception as e:
        print(f"❌ GSC API error: {e}")
        print("Using sample data instead...")
        return get_sample_data()


def get_sample_data():
    """
    Returns FAKE sample data for testing
    Use this when you don't have GSC set up yet
    
    This lets you see the dashboard working even without real Google data
    """
    return [
        {"query": "web design Chennai", "page": "/web-design-chennai.html",
         "clicks": 45, "impressions": 1200, "ctr": 3.75, "position": 8.2},
        {"query": "SEO services Mumbai", "page": "/seo-services-mumbai.html",
         "clicks": 38, "impressions": 980, "ctr": 3.88, "position": 6.5},
        {"query": "digital marketing Delhi", "page": "/digital-marketing-delhi.html",
         "clicks": 62, "impressions": 2100, "ctr": 2.95, "position": 11.3},
        {"query": "web design Bangalore", "page": "/web-design-bangalore.html",
         "clicks": 71, "impressions": 1850, "ctr": 3.84, "position": 5.7},
        {"query": "app development Hyderabad", "page": "/app-development-hyderabad.html",
         "clicks": 29, "impressions": 750, "ctr": 3.87, "position": 9.1},
        {"query": "SEO services Chennai", "page": "/seo-services-chennai.html",
         "clicks": 55, "impressions": 1420, "ctr": 3.87, "position": 7.3},
        {"query": "web design Madurai", "page": "/web-design-madurai.html",
         "clicks": 18, "impressions": 420, "ctr": 4.29, "position": 4.2},
        {"query": "digital marketing Bangalore", "page": "/digital-marketing-bangalore.html",
         "clicks": 83, "impressions": 2600, "ctr": 3.19, "position": 12.8},
    ]


def analyze_rankings(data):
    """
    Analyzes the GSC data and creates a report
    
    Groups data into:
    - Top 3: Position 1-3 (excellent!)
    - Top 10: Position 4-10 (good)
    - Top 20: Position 11-20 (okay)
    - Below 20: Needs work
    """
    if not data:
        return {}
    
    analysis = {
        "total_queries": len(data),
        "total_clicks": sum(r['clicks'] for r in data),
        "total_impressions": sum(r['impressions'] for r in data),
        "top_3": [r for r in data if r['position'] <= 3],
        "top_10": [r for r in data if 3 < r['position'] <= 10],
        "top_20": [r for r in data if 10 < r['position'] <= 20],
        "below_20": [r for r in data if r['position'] > 20],
        "best_pages": sorted(data, key=lambda x: x['clicks'], reverse=True)[:5],
        "avg_position": round(sum(r['position'] for r in data) / len(data), 1)
    }
    
    return analysis


# Run directly for testing
if __name__ == "__main__":
    print("🔍 GSC Tracker Test")
    print("Using sample data (add credentials.json for real data)")
    
    data = get_sample_data()
    analysis = analyze_rankings(data)
    
    print(f"\n📊 Analysis Results:")
    print(f"Total keywords tracked: {analysis['total_queries']}")
    print(f"Total clicks: {analysis['total_clicks']}")
    print(f"Total impressions: {analysis['total_impressions']}")
    print(f"Average position: {analysis['avg_position']}")
    print(f"\n🏆 Top 3 positions: {len(analysis['top_3'])} keywords")
    print(f"✅ Top 10 positions: {len(analysis['top_10'])} keywords")
    print(f"📈 Top 20 positions: {len(analysis['top_20'])} keywords")