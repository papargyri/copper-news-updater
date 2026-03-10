import feedparser
import json
import os
import time
from datetime import datetime, timedelta
import urllib.parse
# The Original 7 Elite Financial Outlets
PREMIUM_OUTLETS = {
    "Financial Times", "The Economist", "The Wall Street Journal", 
    "Reuters", "Bloomberg", "The New York Times", "The Guardian"
}

# 93 Additional Global & Industry Outlets (Total = 100)
GLOBAL_OUTLETS = {
    # Top 50 Core
    "CNBC", "Forbes", "Fortune", "Business Insider", "MarketWatch", "Motley Fool",
    "Seeking Alpha", "Yahoo Finance", "Investopedia", "TheStreet",
    "BBC", "CNN", "Daily Mail", "Fox News", "Al Jazeera", "AP News", "NBC News", 
    "The Washington Post", "USA Today", "MSN", "Yahoo News", "Google News", "NPR", 
    "CBS News", "ABC News", "Time", "Newsweek", "The Telegraph", "The Independent", 
    "South China Morning Post", "Hindustan Times", "The Times of India", 
    "Sydney Morning Herald", "The Globe and Mail", "Le Monde", "Der Spiegel", 
    "El País", "Asahi Shimbun", "Substack", "Axios", "Politico", "HuffPost", "BuzzFeed News",
    
    # 50 Tier-2, Regional, and Mining Trade Journals
    "Mining.com", "The Northern Miner", "Australian Financial Review", "Mining Weekly",
    "Engineering and Mining Journal", "MINING magazine", "Canadian Mining Journal",
    "S&P Global", "Wood Mackenzie", "Fitch Solutions", "Fastmarkets", "Argus Media",
    "Metal Bulletin", "Kitco News", "Cru Group", "Platts", "Eurasia Group",
    "The Australian", "National Post", "Toronto Star", "Vancouver Sun",
    "Folha de S.Paulo", "O Globo", "La Nación", "Clarín", "El Mercurio", "La Tercera",
    "Business Day (South Africa)", "The Star (Kenya)", "New Straits Times", "Jakarta Post",
    "Bangkok Post", "Straits Times", "The Star (Malaysia)", "Philippine Daily Inquirer",
    "Nikkei Asia", "The Japan Times", "Korea JoongAng Daily", "The Chosun Ilbo",
    "Al Arabiya", "Gulf News", "The National (UAE)", "Jerusalem Post", "Haaretz",
    "Sky News", "ITV News", "Channel 4 News", "France 24", "Deutsche Welle", "RT"
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
            # Rebuilding structure to hold separate counters rather than massive article arrays to save space
            json_data[start_str] = {
                "price_usd": None, 
                "premium_count": 0, 
                "global_count": 0
            }
            
        current_day_data = dict(json_data[start_str])
            
        # 1. Fetch Historical Price
        if current_day_data.get("price_usd") is None:
            price = fetch_copper_price_for_date(start_str)
            if price:
                current_day_data["price_usd"] = round(price, 4)
                
        # 2. Fetch Historical News (No URL duplicate checking needed since we rely on strict daily bounds)
        prem_daily = 0
        glob_daily = 0
        
        query = f'("copper mining" OR "copper market" OR "copper price" OR "copper supply demand") after:{start_str} before:{end_str}'
        safe_query = urllib.parse.quote_plus(query)
        rss_url = f"https://news.google.com/rss/search?q={safe_query}&hl=en-US&gl=US&ceid=US:en"
        
        try:
            feed = feedparser.parse(rss_url)
            for entry in feed.entries:
                source_title = str(entry.get('source', {}).get('title', 'Unknown'))
                
                is_premium = any(t.lower() in source_title.lower() for t in PREMIUM_OUTLETS)
                is_global = any(t.lower() in source_title.lower() for t in GLOBAL_OUTLETS)
                
                if is_premium:
                    prem_daily += 1
                elif is_global:
                    glob_daily += 1
        except Exception as e:
            print(f"  Error parsing feed: {e}")
            
        time.sleep(0.5)
        
        # Aggregate the numbers
        # global_count represents ALL top 50 (Premium 7 + Global 43)
        current_day_data["premium_count"] = prem_daily
        current_day_data["global_count"] = prem_daily + glob_daily
        json_data[start_str] = current_day_data
            
        print(f"  -> Found {prem_daily} premium, {prem_daily + glob_daily} total global.")
        
        # Save incrementally
        with open(JSON_PATH, 'w', encoding='utf-8') as f:
            json.dump(json_data, f, indent=4)
            
        current_date = next_date

    print("\nBackfill complete!")

if __name__ == "__main__":
    backfill()
