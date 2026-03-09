import re
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta

# 1. Parse daily article counts from copper_news_summary.md
try:
    with open('copper_news_summary.md', 'r') as f:
        content = f.read()
except FileNotFoundError:
    print("Error: Could not find copper_news_summary.md")
    exit(1)

# Pattern to match the date in the article entries
# e.g.: - *Source: Bloomberg | Date: 2026-03-06 10:07*
pattern = re.compile(r'\s*-\s+\*Source:.*?\|\s*Date:\s*(\d{4}-\d{2}-\d{2})\s*\d{2}:\d{2}\*')

dates = []
for match in pattern.finditer(content):
    dates.append(match.group(1))

# Also count static articles which have a different format:
# - **[Amazon Buying First New US Copper Output](link)** (Jan 15, 2026) – Focus on AI data center demand.
static_pattern = re.compile(r'-\s+\*\*(.*?)\*\*.*?\((.*? \d{1,2}, \d{4})\)')
for match in static_pattern.finditer(content):
    date_str = match.group(2)
    try:
        dt = datetime.strptime(date_str, '%b %d, %Y')
        dates.append(dt.strftime('%Y-%m-%d'))
    except ValueError:
        pass


# Create DataFrame of daily counts
counts = pd.Series(dates).value_counts().reset_index()
counts.columns = ['Date', 'Article_Count']
counts['Date'] = pd.to_datetime(counts['Date'])
counts = counts.sort_values('Date')


# 2. Fetch daily copper prices (HG=F) for the relevant period
min_date = counts['Date'].min() - pd.Timedelta(days=7) # Get a week extra buffer
max_date = counts['Date'].max() + pd.Timedelta(days=7)

copper = yf.Ticker("HG=F")
price_data = copper.history(start=min_date.strftime('%Y-%m-%d'), end=max_date.strftime('%Y-%m-%d'))
price_data.reset_index(inplace=True)
price_data['Date'] = pd.to_datetime(price_data['Date'].dt.tz_localize(None).dt.strftime('%Y-%m-%d'))

price_df = price_data[['Date', 'Close']].rename(columns={'Close': 'Copper_Price_USD'})

# Calculate percentage returns for the price
price_df['Price_Return_1D'] = price_df['Copper_Price_USD'].pct_change()
price_df['Price_Return_3D'] = price_df['Copper_Price_USD'].pct_change(periods=3)


# 3. Merge data
# We merge using an outer join to keep all trading days, then fill missing article counts with 0
merged_df = pd.merge(price_df, counts, on='Date', how='left')
merged_df['Article_Count'] = merged_df['Article_Count'].fillna(0)


# 4. Correlation Analysis
print("=== Short-Term Daily Correlation Analysis: News vs Copper Price ===\n")

# A. Same-Day Correlation
same_day_corr = merged_df['Article_Count'].corr(merged_df['Price_Return_1D'])
print(f"Same-Day Correlation (News Volume vs. Same Day Price Return): {same_day_corr:.4f}")

# B. News Leading Indicator (Does news predict TOMORROW's price?)
# We shift the price return backwards (so today's news aligns with tomorrow's return)
merged_df['Next_Day_Return'] = merged_df['Price_Return_1D'].shift(-1)
news_leads_1d_corr = merged_df['Article_Count'].corr(merged_df['Next_Day_Return'])
print(f"News Leading (1 Day) Correlation (News today vs Tomorrow's Return): {news_leads_1d_corr:.4f}")

# C. News Leading Indicator (Does news predict the NEXT 3 DAYS return?)
merged_df['Next_3D_Return'] = merged_df['Price_Return_3D'].shift(-3)
news_leads_3d_corr = merged_df['Article_Count'].corr(merged_df['Next_3D_Return'])
print(f"News Leading (3 Day) Correlation (News today vs Next 3 Days Return): {news_leads_3d_corr:.4f}")

# D. Price Leading Indicator (Do price changes yesterday cause news coverage TODAY?)
merged_df['Prev_Day_Return'] = merged_df['Price_Return_1D'].shift(1)
price_leads_corr = merged_df['Article_Count'].corr(merged_df['Prev_Day_Return'])
print(f"Price Leading Correlation (Yesterday's Return vs News today): {price_leads_corr:.4f}")

print("\n--- Summary ---")

def interpret(corr, name):
    if abs(corr) < 0.2:
        return f"{name}: Very weak or no correlation ({corr:.4f})."
    elif abs(corr) < 0.4:
        return f"{name}: Weak correlation ({corr:.4f})."
    else:
        return f"{name}: Moderate/Strong correlation ({corr:.4f})."

print(interpret(same_day_corr, "Same Day"))
print(interpret(news_leads_1d_corr, "News predicts Tomorrow's Price"))
print(interpret(news_leads_3d_corr, "News predicts Next 3 Days Price"))
print(interpret(price_leads_corr, "Price predicts Tomorrow's News"))

# Save the raw data for transparency
merged_df.to_csv("data/daily_lag_correlation_report.csv", index=False)
print("\nRaw data saved to data/daily_lag_correlation_report.csv")
