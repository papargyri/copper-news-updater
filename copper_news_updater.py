import feedparser
import requests
import os
from datetime import datetime, timedelta
import time

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

def update_summary_file(articles):
    # Use relative path for GitHub Actions
    summary_path = "copper_news_summary.md"
    
    if not articles:
        print("No new articles found.")
        return

    # Prepare the update content
    update_header = f"## 🔄 Latest Updates (as of {datetime.now().strftime('%Y-%m-%d %H:%M')})\n\n"
    article_list = ""
    for art in articles:
        article_list += f"- **[{art['title']}]({art['link']})**\n  - *Source: {art['source']} | Date: {art['date']}*\n"
    
    article_list += "\n---\n"

    try:
        with open(summary_path, "r") as f:
            content = f.read()
        
        # Insert updates after the main market overview
        marker = "---"
        parts = content.split(marker, 1)
        
        if len(parts) > 1:
            new_content = parts[0] + marker + "\n\n" + update_header + article_list + parts[1]
        else:
            new_content = content + "\n\n" + update_header + article_list

        with open(summary_path, "w") as f:
            f.write(new_content)
        
        print(f"Successfully updated {summary_path} with {len(articles)} new articles.")
    except Exception as e:
        print(f"Error updating file: {e}")

if __name__ == "__main__":
    print("Starting copper news update...")
    new_articles = fetch_copper_news()
    update_summary_file(new_articles)
    print("Update complete.")
