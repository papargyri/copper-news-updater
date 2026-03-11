import json
import pandas as pd
import numpy as np

def load_data():
    with open('data/articles_by_date.json', 'r') as f:
        data = json.load(f)
    
    records = []
    for date_str, info in data.items():
        records.append({
            'date': pd.to_datetime(date_str),
            'price_usd': info.get('price_usd'),
            'global_count': info.get('global_count', 0)
        })
    
    df = pd.DataFrame(records)
    df = df[df['price_usd'].notna()].copy()
    df.sort_values('date', inplace=True)
    df.reset_index(drop=True, inplace=True)
    return df

def analyze_trade_timing(df):
    results = []
    
    # Calculate price change ON THE DAY the news hits (T=0 to T=0)
    # Since we only have daily close data, we compare T-1 close to T=0 close
    df['price_change_T0'] = df['price_usd'] / df['price_usd'].shift(1) - 1
    
    # Calculate price change on T+1 (T=0 close to T+1 close)
    df['price_change_T1'] = df['price_usd'].shift(-1) / df['price_usd'] - 1
    
    # Calculate price change on T+2 (T+1 close to T+2 close)
    df['price_change_T2'] = df['price_usd'].shift(-2) / df['price_usd'].shift(-1) - 1
    
    df_clean = df.dropna(subset=['price_change_T0', 'price_change_T1', 'price_change_T2']).copy()
    
    patterns = []
    patterns.append("# ⏱️ Trade Feasibility & Timing Analysis\n")
    patterns.append("This report investigates whether there is enough time to actually buy copper *after* the news breaks, or if the market has already reacted.\n")
    
    # Focus on Spike Days (Top 20% of news volume)
    threshold = df_clean['global_count'].quantile(0.8)
    spikes_df = df_clean[df_clean['global_count'] >= threshold]
    normal_df = df_clean[df_clean['global_count'] < threshold]
    
    patterns.append("## Price Action Around a News Spike (>6 articles)\n")
    patterns.append(f"We analyzed {len(spikes_df)} days with high news volume to see exactly *when* the price moves.\n")
    
    t0_return = spikes_df['price_change_T0'].mean() * 100
    t1_return = spikes_df['price_change_T1'].mean() * 100
    t2_return = spikes_df['price_change_T2'].mean() * 100
    
    patterns.append(f"- **Day 0 (The day the articles are published):** {t0_return:.2f}% return during the day")
    patterns.append(f"- **Day 1 (The day after publication):** {t1_return:.2f}% return")
    patterns.append(f"- **Day 2:** {t2_return:.2f}% return\n")
    
    if t0_return > t1_return and t0_return > 0:
        patterns.append("**Conclusion:** The market reacts *immediately*. On days when lots of news is published, the price jumps significantly *that same day* (Day 0). If you read the news at the end of the day or the next morning, you have already missed the core upward movement, and you are buying into the subsequent flatline/decay (Day 1 & Day 2).")
    else:
        patterns.append("**Conclusion:** There remains a delayed reaction. The largest portion of the move happens on the days *following* the news spike.")

    with open('trade_timing_report.md', 'w') as f:
        f.write('\n'.join(patterns))
        
    print("Timing analysis complete. Check trade_timing_report.md for findings.")

if __name__ == "__main__":
    df = load_data()
    analyze_trade_timing(df)
