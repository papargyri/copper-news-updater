import json
import pandas as pd
import numpy as np
from scipy import stats
from textblob import TextBlob
import ssl
import urllib.request

# Bypass SSL restriction for NLTK corporas
try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context

import nltk
nltk.download('punkt', quiet=True)
nltk.download('punkt_tab', quiet=True)

def analyze_sentiment(title):
    blob = TextBlob(title)
    return blob.sentiment.polarity # -1 to 1 (negative to positive)

def load_data_with_sentiment():
    with open('data/articles_by_date.json', 'r') as f:
        data = json.load(f)
    
    records = []
    for date_str, info in data.items():
        daily_sentiment = 0
        total_articles = info.get('global_count', 0)
        
        # Calculate average sentiment for the day from the available articles
        articles = info.get('articles', [])
        if articles:
            sentiments = [analyze_sentiment(art['title']) for art in articles]
            daily_sentiment = np.mean(sentiments)
            
        records.append({
            'date': pd.to_datetime(date_str),
            'price_usd': info.get('price_usd'),
            'global_count': total_articles,
            'daily_sentiment': daily_sentiment
        })
    
    df = pd.DataFrame(records)
    df = df[df['price_usd'].notna()].copy()
    df.sort_values('date', inplace=True)
    df.reset_index(drop=True, inplace=True)
    return df

def analyze_sentiment_correlations(df):
    results = []
    
    # Smooth sentiment (3-day rolling average)
    df['sentiment_smooth'] = df['daily_sentiment'].rolling(window=3, min_periods=1).mean()
    
    # Calculate forward price percentage changes
    df['price_fwd_1d'] = df['price_usd'].shift(-1) / df['price_usd'] - 1
    df['price_fwd_2d'] = df['price_usd'].shift(-2) / df['price_usd'] - 1
    df['price_fwd_3d'] = df['price_usd'].shift(-3) / df['price_usd'] - 1
    
    df_clean = df.dropna(subset=['price_fwd_1d', 'price_fwd_2d', 'price_fwd_3d', 'daily_sentiment']).copy()
    
    patterns = []
    patterns.append("# 🧠 Copper News Sentiment vs. Price Correlation Analysis\n")
    patterns.append("This report calculates the statistical relationship between the **NLP sentiment** of copper news articles (is the news positive/bullish or negative/bearish?) vs. the copper price movements over the next 1 to 3 days.\n")
    
    patterns.append("## 1. Linear Correlations (Pearson)\n")
    patterns.append("A correlation of 1 means perfect positive correlation (positive news = price goes up), -1 means perfect negative correlation (positive news = price crashes).\n")
    
    signals = ['daily_sentiment', 'sentiment_smooth']
    horizons = [('1 Day Later', 'price_fwd_1d'), ('2 Days Later', 'price_fwd_2d'), ('3 Days Later', 'price_fwd_3d')]
    
    for signal in signals:
        patterns.append(f"### Signal: `{signal}`")
        for h_name, h_col in horizons:
            corr, p_value = stats.pearsonr(df_clean[signal], df_clean[h_col])
            patterns.append(f"- **{h_name}**: Correlation = {corr:.3f} (p-value: {p_value:.3f})")
            if p_value < 0.05:
                patterns.append(f"  - *Statistically significant!*")
        patterns.append("")
        
    patterns.append("## 2. Bullish vs Bearish News Days Simulation\n")
    
    # Define strongly positive and negative days
    bullish_days = df_clean[df_clean['daily_sentiment'] > 0.1]
    bearish_days = df_clean[df_clean['daily_sentiment'] < -0.1]
    neutral_days = df_clean[(df_clean['daily_sentiment'] >= -0.1) & (df_clean['daily_sentiment'] <= 0.1)]
    
    patterns.append(f"**Day Classifications:** Bullish ({len(bullish_days)}), Bearish ({len(bearish_days)}), Neutral ({len(neutral_days)})\n")
    
    for h_name, h_col in horizons:
        bull_return = bullish_days[h_col].mean() * 100
        bear_return = bearish_days[h_col].mean() * 100
        neutral_return = neutral_days[h_col].mean() * 100
        
        patterns.append(f"### {h_name} Average Price Change")
        patterns.append(f"- **After highly POSITIVE news:** {bull_return:.2f}%")
        patterns.append(f"- **After highly NEGATIVE news:** {bear_return:.2f}%")
        patterns.append(f"- **After NEUTRAL news:** {neutral_return:.2f}%")
        
        if bull_return > bear_return:
            patterns.append("  - *Observation: Positive news precedes stronger performance than negative news (Intuitive!)*")
        elif bull_return < bear_return:
            patterns.append("  - *Observation: Negative news precedes stronger performance than positive news (Contrarian!)*")
        patterns.append("")

    with open('sentiment_analysis_report.md', 'w') as f:
        f.write('\n'.join(patterns))
        
    print("Sentiment analysis complete. Check sentiment_analysis_report.md for findings.")

if __name__ == "__main__":
    df = load_data_with_sentiment()
    analyze_sentiment_correlations(df)
