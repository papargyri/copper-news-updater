import feedparser
import json
import os
import time
from datetime import datetime, timedelta
import urllib.parse
import yfinance as yf
import pandas as pd

# Target Outlets
TARGET_OUTLETS = {
    "Financial Times", "The Economist", "The Guardian", 
    "The New York Times", "The Wall Street Journal", 
    "Reuters", "Bloomberg"
}

JSON_PATH = "data/articles_by_date.json"

def fetch_copper_price_for_date(date_str):
    """Fetch the close price of HG=F for a specific date."""
    try:
        copper = yf.Ticker("HG=F")
        # Add 1 day to end to ensure the start date is included in the fetch
        end_date = (datetime.strptime(date_str, '%Y-%m-%d') + timedelta(days=2)).strftime('%Y-%m-%d')
        start_date = (datetime.strptime(date_str, '%Y-%m-%d') - timedelta(days=5)).strftime('%Y-%m-%d')
        
        hist = copper.history(start=start_date, end=end_date)
        if not hist.empty:
            # Find the closest trading day on or before the target date
            hist.index = hist.index.tz_localize(None)
            target_dt = pd.to_datetime(date_str)
            past_prices = hist[hist.index <= target_dt]
            if not past_prices.empty:
                return float(past_prices['Close'].iloc[-1])
    except Exception as e:
        print(f"Price fetch error for {date_str}: {e}")
    return None

def backfill():
    print("Starting 2025 Daily Backfill (Jan 1, 2025 -> Today)...")
    
    # Load existing JSON
    if os.path.exists(JSON_PATH):
        with open(JSON_PATH, 'r', encoding='utf-8') as f:
            json_data = json.load(f)
    else:
        json_data = {}

    start_date = datetime(2025, 1, 1)
    end_date = datetime.now()
    
    current_date = start_date
    
    while current_date <= end_date:
        next_date = current_date + timedelta(days=1)
        
        start_str = current_date.strftime('%Y-%m-%d')
        end_str = next_date.strftime('%Y-%m-%d')
        
        print(f"Fetching data for: {start_str}")
        
        if start_str not in json_data:
            json_data[start_str] = {"price_usd": None, "articles": []}
            
        current_day_data = dict(json_data[start_str])
            
        # 1. Fetch Historical Price
        if current_day_data["price_usd"] is None:
            price = fetch_copper_price_for_date(start_str)
            if price:
                current_day_data["price_usd"] = round(price, 4)
                
        # 2. Fetch Historical News
        article_list = list(current_day_data.get("articles", []))
        existing_urls = [str(a['link']) for a in article_list if 'link' in a]
        found_today = 0
        
        # Combine all queries into one expression using OR to drastically speed up the fetch
        query = f'("copper mining" OR "copper market" OR "copper price" OR "copper supply demand") after:{start_str} before:{end_str}'
        safe_query = urllib.parse.quote_plus(query)
        rss_url = f"https://news.google.com/rss/search?q={safe_query}&hl=en-US&gl=US&ceid=US:en"
        
        try:
            feed = feedparser.parse(rss_url)
            for entry in feed.entries:
                source_title = str(entry.get('source', {}).get('title', 'Unknown'))
                is_target = any(target.lower() in source_title.lower() for target in TARGET_OUTLETS)
                
                entry_link = str(entry.link)
                if is_target and entry_link not in existing_urls:
                    pub_parsed = entry.get('published_parsed')
                    if pub_parsed:
                        pub_dt = datetime.fromtimestamp(time.mktime(pub_parsed))
                        
                        article_list.append({
                            'title': str(entry.title),
                            'link': entry_link,
                            'date': pub_dt.strftime('%Y-%m-%d %H:%M'),
                            'source': source_title
                        })
                        existing_urls.append(entry_link)
                        found_today += 1
        except Exception as e:
            print(f"  Error parsing feed: {e}")
            
        time.sleep(0.5) # Be nice to Google
        
        current_day_data["articles"] = article_list
        json_data[start_str] = current_day_data
            
        print(f"  -> Found {found_today} new premium articles.")
        
        # Save incrementally
        with open(JSON_PATH, 'w', encoding='utf-8') as f:
            json.dump(json_data, f, indent=4)
            
        current_date = next_date

    print("\nBackfill complete!")

if __name__ == "__main__":
    backfill()
