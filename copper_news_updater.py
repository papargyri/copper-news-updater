import feedparser
import requests
import os
import json
import yfinance as yf
from datetime import datetime, timedelta
import time
from generate_interactive_chart import generate_interactive_chart

def fetch_copper_news():
    # Google News RSS feeds for copper-related terms
    queries = ["copper mining", "copper market", "copper price", "copper supply demand"]
    articles = []
    seen_urls = set()

    # Target outlets specified by the user
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

    # Time window: last 3 days
    three_days_ago = datetime.now() - timedelta(days=3)

    for query in queries:
        rss_url = f"https://news.google.com/rss/search?q={query.replace(' ', '+')}&hl=en-US&gl=US&ceid=US:en"
        feed = feedparser.parse(rss_url)
        
        for entry in feed.entries:
            published_parsed = entry.get('published_parsed')
            if published_parsed:
                pub_date = datetime.fromtimestamp(time.mktime(published_parsed))
                source_title = str(entry.get('source', {}).get('title', 'Unknown'))
                
                is_premium = any(t.lower() in source_title.lower() for t in PREMIUM_OUTLETS)
                is_global = any(t.lower() in source_title.lower() for t in GLOBAL_OUTLETS)

                entry_link = str(entry.link)
                
                if pub_date > three_days_ago and entry_link not in seen_urls and (is_premium or is_global):
                    articles.append({
                        'title': str(entry.title),
                        'link': entry_link,
                        'date': pub_date.strftime('%Y-%m-%d %H:%M'),
                        'source': source_title,
                        'is_premium': is_premium
                    })
                    seen_urls.add(entry_link)
    
    return sorted(articles, key=lambda x: x['date'], reverse=True)

def fetch_daily_copper_price():
    """Fetches the latest closing price of Copper Futures (HG=F) using yfinance."""
    print("Fetching today's copper futures price (HG=F)...")
    try:
        copper = yf.Ticker("HG=F")
        # Get the last 5 days to ensure we get the most recent trading close (skips weekends/holidays)
        hist = copper.history(period="5d")
        if not hist.empty:
            latest_close = float(hist['Close'].iloc[-1])
            latest_date = hist.index[-1].strftime('%Y-%m-%d')
            print(f"Latest Copper Price ({latest_date}): ${latest_close:.4f}")
            return {"date": latest_date, "price_usd": round(latest_close, 4)}
        else:
            print("Warning: Could not fetch copper price data (empty result).")
            return None
    except Exception as e:
        print(f"Error fetching copper price: {e}")
        return None

def update_summary_file(articles):
    # Use relative path for GitHub Actions
    summary_path = "copper_news_summary.md"
    
    # Ensure data directory exists
    os.makedirs(os.path.dirname("data/articles_by_date.json"), exist_ok=True)
    
    try:
        with open(summary_path, "r", encoding="utf-8") as f:
            content = f.read()
    except FileNotFoundError:
        content = ""

    # Filter out articles that are already present in the summary file
    new_articles = [art for art in articles if art['link'] not in content]
    print(f"Total articles fetched from RSS (last 3 days): {len(articles)}")
    print(f"Total new articles after filtering duplicates: {len(new_articles)}")

    # Fetch price once for both markdown and JSON updates
    price_data = fetch_daily_copper_price()
    latest_price_value = price_data["price_usd"] if price_data else None

    update_json_datastore(new_articles, latest_price_value)
    
    new_premium_articles = [art for art in new_articles if art.get('is_premium', False)]

    if not new_premium_articles:
        print("No new premium articles to add to Markdown. All fetched premium articles are already in the summary.")
        return

    # Prepare the update content for markdown
    update_header = f"## 🔄 Latest Updates (as of {datetime.now().strftime('%Y-%m-%d %H:%M')})\n\n"
    article_list = ""
    for art in new_premium_articles:
        article_list += f"- **[{art['title']}]({art['link']})**\n  - *Source: {art['source']} | Date: {art['date']}*\n"
    
    article_list += "\n---\n"

    try:
        # Insert updates after the main market overview
        marker = "---"
        parts = content.split(marker, 1)
        
        if len(parts) > 1:
            new_content = parts[0] + marker + "\n\n" + update_header + article_list + parts[1]
        else:
            new_content = content + "\n\n" + update_header + article_list

        with open(summary_path, "w", encoding="utf-8") as f:
            f.write(new_content)
        
        print(f"Successfully updated {summary_path} with {len(new_articles)} new articles.")
    except Exception as e:
        print(f"Error updating file: {e}")

def update_json_datastore(new_articles, latest_price):
    """
    Updates a structured JSON file that maps each date to its exact copper price 
    and the distinct volume of Premium (Top 7) vs Total Global (Top 50) articles.
    """
    json_path = "data/articles_by_date.json"
    
    if os.path.exists(json_path):
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    else:
        data = {}

    today_str = datetime.now().strftime('%Y-%m-%d')
    
    if today_str not in data:
        data[today_str] = {
            "price_usd": None, 
            "premium_count": 0,
            "global_count": 0
        }
        
    current_day = dict(data[today_str])

    # 1. Update Price
    if latest_price:
        current_day["price_usd"] = round(latest_price, 4)

    # 2. Update Article Counts (Count only what was fetched today for today)
    prem_today = sum(1 for a in new_articles if a.get('is_premium', False))
    glob_today = len(new_articles) - prem_today
    
    # Since this script runs daily, we just add the newly scraped articles to the running tally
    prev_prem = current_day.get('premium_count', 0) if isinstance(current_day.get('premium_count'), int) else 0
    prev_glob = current_day.get('global_count', 0) if isinstance(current_day.get('global_count'), int) else 0
    
    current_day["premium_count"] = prev_prem + prem_today
    current_day["global_count"] = prev_glob + prem_today + glob_today

    data[today_str] = current_day

    # Save
    os.makedirs(os.path.dirname(json_path), exist_ok=True)
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4)
        
    print(f"Successfully updated structured datastore: {json_path}")

if __name__ == "__main__":
    print("Starting copper news update...")
    fetched_articles = fetch_copper_news()
    update_summary_file(fetched_articles)
    
    # Generate the updated interactive chart with the latest data
    try:
        generate_interactive_chart()
    except Exception as e:
        print(f"Error generating chart: {e}")
        
    print("Update complete.")
