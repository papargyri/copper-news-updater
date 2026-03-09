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
    target_outlets = {
        "Financial Times", "The Economist", "The Guardian", 
        "The New York Times", "The Wall Street Journal", 
        "Reuters", "Bloomberg"
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
                source_title = entry.get('source', {}).get('title', 'Unknown')
                
                # Check if the source matches our target outlets (case-insensitive partial match)
                is_target_source = any(target.lower() in source_title.lower() for target in target_outlets)

                if pub_date > three_days_ago and entry.link not in seen_urls and is_target_source:
                    articles.append({
                        'title': entry.title,
                        'link': entry.link,
                        'date': pub_date.strftime('%Y-%m-%d %H:%M'),
                        'source': source_title
                    })
                    seen_urls.add(entry.link)
    
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
    json_path = "data/articles_by_date.json"
    
    # Ensure data directory exists
    os.makedirs(os.path.dirname(json_path), exist_ok=True)
    
    try:
        with open(summary_path, "r", encoding="utf-8") as f:
            content = f.read()
    except FileNotFoundError:
        content = ""

    # Filter out articles that are already present in the summary file
    new_articles = [art for art in articles if art['link'] not in content]
    print(f"Total articles fetched from RSS (last 3 days): {len(articles)}")
    print(f"Total new articles after filtering duplicates: {len(new_articles)}")

    update_json_datastore(new_articles, json_path)

    if not new_articles:
        print("No new articles to add to Markdown. All fetched articles are already in the summary.")
        return

    # Prepare the update content for markdown
    update_header = f"## 🔄 Latest Updates (as of {datetime.now().strftime('%Y-%m-%d %H:%M')})\n\n"
    article_list = ""
    for art in new_articles:
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

def update_json_datastore(new_articles, json_path):
    """Updates the JSON file with new articles and the latest copper price."""
    # Fetch today's price
    price_data = fetch_daily_copper_price()
    today_str = datetime.now().strftime('%Y-%m-%d')
    price_date = price_data['date'] if price_data else today_str
    
    # We log data under the price's trading date to align markets with news
    target_date = price_date

    try:
        if os.path.exists(json_path):
            with open(json_path, 'r', encoding='utf-8') as f:
                json_data = json.load(f)
        else:
            json_data = {}
            
        # Ensure the date entry exists
        if target_date not in json_data:
            json_data[target_date] = {"price_usd": None, "articles": []}
            
        # Update the price if we successfully fetched it
        if price_data:
             json_data[target_date]["price_usd"] = price_data["price_usd"]
            
        # Append any new articles
        article_list = json_data[target_date].get("articles", [])
        extracted_urls = [a['link'] for a in article_list]
        for art in new_articles:
            # Prevent duplicates inside the JSON array just in case
            if art['link'] not in extracted_urls:
                 article_list.append(art)
                 extracted_urls.append(art['link'])
                 
        json_data[target_date]["articles"] = article_list
            
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(json_data, f, indent=4)
        print(f"Successfully updated structured datastore: {json_path}")
    except Exception as e:
        print(f"Error updating JSON datastore: {e}")

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
