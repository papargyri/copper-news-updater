# 🤖 News Fetching Automation Research

As part of the request to automate copper news updates, research was conducted on fetching articles programmatically from premium outlets like the Financial Times, The Economist, and Reuters.

## 🐍 Python Libraries and Approaches

### 1. RSS Feed Parsers
- **`feedparser`**: Standard library for RSS and Atom feeds. Requires finding the specific RSS URL for each outlet.
- **`feedsearch-crawler`**: Useful for automatically finding RSS URLs on a website.

### 2. General News Scraping
- **`Newspaper3k`**: High-level library for extracting article text, authors, dates, and summaries. Good for general news sites but may struggle with paywalls.
- **`newspaper-scraper`**: Unified interface that can handle both public and paywalled content using BeautifulSoup and Selenium.

### 3. Commercial News APIs
- **News API (`newsapi-python`)**: Broad access to headlines and articles across 30k+ sources using a single API key.
- **PyGoogleNews**: Unofficial Python wrapper for Google News RSS feeds.

### 4. Specific Outlet Strategies
| Outlet | Method |
| :--- | :--- |
| **Financial Times** | **dltHub** (REST API source) - requires specific FT license and API key. |
| **The Economist** | No direct public API. **Selenium/Playwright** is suggested to mimic browser behavior. |
| **Reuters** | **Refinitiv Eikon Data API** (commercial) or **Apify's Reuters News API** (scraping service). |

## ⚙️ Scheduling Mechanisms
- **Cron (macOS/Unix)**: Traditional, lightweight scheduling for scripts.
- **Launchd (macOS)**: Native macOS system for managing daemons and background tasks.
- **GitHub Actions (Recommended ✅)**: The most robust approach. Automates the script on GitHub's servers every day (e.g., at 6:00 AM UTC). It eliminates the need for your local computer to be awake and connected.
- **Final Choice (Daily at 6 AM)**: `0 6 * * *` (runs every day at 6:00 AM) to update the copper news summary report automatically.

---

## ⚠️ Compliance Note
When implementing scraping automation, respect the website's `robots.txt` and terms of service to avoid IP blocking and ensure legal compliance. Accessing premium content (FT, Economist) typically requires a valid subscription and potentially specific API access agreements.
