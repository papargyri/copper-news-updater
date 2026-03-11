import json
import pandas as pd
import numpy as np
from scipy import stats

def load_data():
    with open('data/articles_by_date.json', 'r') as f:
        data = json.load(f)
    
    records = []
    for date_str, info in data.items():
        records.append({
            'date': pd.to_datetime(date_str),
            'price_usd': info.get('price_usd'),
            'premium_count': info.get('premium_count', 0),
            'global_count': info.get('global_count', 0)
        })
    
    df = pd.DataFrame(records)
    # Filter out future empty dates
    df = df[df['price_usd'].notna()].copy()
    df.sort_values('date', inplace=True)
    df.reset_index(drop=True, inplace=True)
    return df

def analyze_correlations(df):
    results = []
    
    # Calculate daily changes in news volume
    df['global_change'] = df['global_count'].diff()
    df['premium_change'] = df['premium_count'].diff()
    
    # Calculate forward price percentage changes
    # T+1, T+2, T+3
    df['price_fwd_1d'] = df['price_usd'].shift(-1) / df['price_usd'] - 1
    df['price_fwd_2d'] = df['price_usd'].shift(-2) / df['price_usd'] - 1
    df['price_fwd_3d'] = df['price_usd'].shift(-3) / df['price_usd'] - 1
    
    # Drop rows with NaN (the last few days where we don't have future prices)
    df_clean = df.dropna(subset=['global_change', 'price_fwd_1d', 'price_fwd_2d', 'price_fwd_3d']).copy()
    
    patterns = []
    patterns.append("# 📈 Copper News Volume vs. Price Correlation Analysis\n")
    patterns.append("This report calculates the statistical relationship between the volume of copper news articles (and their daily changes) today vs. the copper price movements over the next 1 to 3 days.\n")
    
    patterns.append("## 1. Linear Correlations (Pearson)\n")
    patterns.append("A correlation of 1 means perfect positive correlation, -1 means perfect negative correlation, and 0 means no correlation.\n")
    
    # Evaluate variables
    signals = ['global_count', 'premium_count', 'global_change', 'premium_change']
    horizons = [('1 Day Later', 'price_fwd_1d'), ('2 Days Later', 'price_fwd_2d'), ('3 Days Later', 'price_fwd_3d')]
    
    for signal in signals:
        patterns.append(f"### Signal: `{signal}`")
        for h_name, h_col in horizons:
            # Calculate correlation
            corr, p_value = stats.pearsonr(df_clean[signal], df_clean[h_col])
            patterns.append(f"- **{h_name}**: Correlation = {corr:.3f} (p-value: {p_value:.3f})")
            if p_value < 0.05:
                patterns.append(f"  - *Statistically significant!*")
        patterns.append("")
        
    patterns.append("## 2. Spike Analysis (Event Study)\n")
    patterns.append("What happens to the price after a notable spike in news articles? Let's define a 'Spike' as a day where the `global_count` is in the top 20% of all days.\n")
    
    threshold = df_clean['global_count'].quantile(0.8)
    spikes_df = df_clean[df_clean['global_count'] >= threshold]
    normal_df = df_clean[df_clean['global_count'] < threshold]
    
    patterns.append(f"**Top 20% Threshold:** {threshold:.1f} articles (Spike days: {len(spikes_df)}, Normal days: {len(normal_df)})\n")
    
    for h_name, h_col in horizons:
        spike_avg_return = spikes_df[h_col].mean() * 100
        normal_avg_return = normal_df[h_col].mean() * 100
        
        patterns.append(f"### {h_name} Average Price Change")
        patterns.append(f"- **After a News Spike:** {spike_avg_return:.2f}%")
        patterns.append(f"- **After Normal Days:** {normal_avg_return:.2f}%")
        if spike_avg_return < normal_avg_return:
            patterns.append("  - *Observation: High news volume tends to precede weaker price performance.*")
        elif spike_avg_return > normal_avg_return:
            patterns.append("  - *Observation: High news volume tends to precede stronger price performance.*")
        patterns.append("")
        
    patterns.append("## 3. Momentum Trading Simulation (Hypothetical)\n")
    patterns.append("If we bought copper when the `global_change` (day-over-day news increase) was highly positive, vs when it dropped, what would the T+2 return look like?\n")
    
    # High increase in news vs drop in news
    news_increase = df_clean[df_clean['global_change'] > 0]
    news_decrease = df_clean[df_clean['global_change'] < 0]
    
    patterns.append(f"- **Average 2-Day Return when News Volume INCREASES (Positive Delta):** {news_increase['price_fwd_2d'].mean() * 100:.2f}%")
    patterns.append(f"- **Average 2-Day Return when News Volume DECREASES (Negative Delta):** {news_decrease['price_fwd_2d'].mean() * 100:.2f}%")

    with open('correlation_analysis_report.md', 'w') as f:
        f.write('\n'.join(patterns))
        
    print("Analysis complete. Check correlation_analysis_report.md for findings.")

if __name__ == "__main__":
    df = load_data()
    analyze_correlations(df)
