import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import feedparser
import time
import requests
import json
import os

# 1. Fetch 1 Year of Copper Futures Prices (HG=F)
print("Fetching 1 year of historical copper futures prices (HG=F)...")
copper = yf.Ticker("HG=F")
end_date = datetime.now()
start_date = end_date - timedelta(days=365)

# Download daily data
price_data = copper.history(start=start_date.strftime('%Y-%m-%d'), end=end_date.strftime('%Y-%m-%d'))
price_data.reset_index(inplace=True)

# Keep only relevant columns and clean up dates
price_data['Date'] = price_data['Date'].dt.tz_localize(None).dt.strftime('%Y-%m-%d')
price_df = price_data[['Date', 'Close']].rename(columns={'Close': 'Copper_Price_USD'})
price_df.to_csv("data/historical_copper_prices.csv", index=False)
print(f"Saved {len(price_df)} days of price data to data/historical_copper_prices.csv")


# 2. Fetch Historical News Volume Estimates
# We can't easily get every article for a whole year via free RSS, but we can do targeted
# Google News searches month-by-month and count the *volume* of hits for our premium outlets.
print("\nFetching historical news volume estimates (this may take a minute)...")

target_outlets = ["Financial Times", "The Economist", "The Wall Street Journal", "Reuters", "Bloomberg"]
monthly_counts = []

for i in range(12):
    # Calculate month window
    m_end = end_date - timedelta(days=30*i)
    m_start = m_end - timedelta(days=30)
    
    start_str = m_start.strftime('%Y-%m-%d')
    end_str = m_end.strftime('%Y-%m-%d')
    month_label = m_start.strftime('%Y-%m')
    
    print(f"  Scanning window: {start_str} to {end_str}")
    
    # Query Google News with date bounds
    query = f"copper market after:{start_str} before:{end_str}"
    rss_url = f"https://news.google.com/rss/search?q={query.replace(' ', '+')}&hl=en-US&gl=US&ceid=US:en"
    
    try:
        feed = feedparser.parse(rss_url)
        
        # Count target outlet hits in this window
        premium_count = 0
        all_count = len(feed.entries)
        
        for entry in feed.entries:
            source = entry.get('source', {}).get('title', 'Unknown')
            if any(target.lower() in source.lower() for target in target_outlets):
                premium_count += 1
                
        monthly_counts.append({
            'Month': month_label,
            'Premium_Articles': premium_count,
            'Total_Articles': all_count
        })
        
        time.sleep(1) # Be nice to the API
        
    except Exception as e:
        print(f"    Error fetching for {month_label}: {e}")

# Save news volume data
news_df = pd.DataFrame(monthly_counts)
news_df.to_csv("data/historical_news_volume.csv", index=False)
print(f"Saved monthly news volume data to data/historical_news_volume.csv")

print("\nHistorical data fetching complete! Ready for correlation analysis.")
