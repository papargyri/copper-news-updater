# 🐍 Copper News Updater Script

This Python script was developed to automate the fetching of recent copper-related news and update the market summary file.

## Script Content

```python
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

    # Time window: last 3 days
    three_days_ago = datetime.now() - timedelta(days=3)

    for query in queries:
        rss_url = f"https://news.google.com/rss/search?q={query.replace(' ', '+')}&hl=en-US&gl=US&ceid=US:en"
        feed = feedparser.parse(rss_url)
        
        for entry in feed.entries:
            published_parsed = entry.get('published_parsed')
            if published_parsed:
                pub_date = datetime.fromtimestamp(time.mktime(published_parsed))
                if pub_date > three_days_ago and entry.link not in seen_urls:
                    articles.append({
                        'title': entry.title,
                        'link': entry.link,
                        'date': pub_date.strftime('%Y-%m-%d %H:%M'),
                        'source': entry.get('source', {}).get('title', 'Unknown')
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
```

## Dependencies (requirements.txt)
```text
feedparser==6.0.11
requests==2.32.3
```

## How It Works
1.  **Fetching**: Uses `feedparser` to parse Google News RSS feeds for specific queries ("copper mining", "copper market", etc.).
2.  **Filtering**: Only retrieves articles published within the last 3 days to maintain relevance.
3.  **Updating**: Reads an existing Markdown summary file, identifies a separator (`---`), and injects the new articles into a "Latest Updates" section.
4.  **Deduplication**: tracks URLs to avoid adding the same article multiple times.
