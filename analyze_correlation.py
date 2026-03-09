import pandas as pd
from scipy.stats import pearsonr

# 1. Load Data
try:
    prices = pd.read_csv("data/historical_copper_prices.csv")
    news = pd.read_csv("data/historical_news_volume.csv")
except FileNotFoundError:
    print("Error: Could not find historical data files.")
    exit(1)

# 2. Prepare Price Data (convert daily to monthly average to match news volume)
prices['Date'] = pd.to_datetime(prices['Date'])
prices['Month'] = prices['Date'].dt.strftime('%Y-%m')

# Calculate monthly average price
monthly_prices = prices.groupby('Month')['Copper_Price_USD'].mean().reset_index()

# 3. Merge Data
# Inner merge on 'Month' (e.g., '2025-09')
merged_df = pd.merge(news, monthly_prices, on='Month', how='inner')

if len(merged_df) < 2:
    print("Not enough overlapping months to calculate correlation.")
    exit(1)

# 4. Correlation Analysis
# We want to see if the volume of Premium Articles correlates with the average monthly price.
corr_coef, p_value = pearsonr(merged_df['Premium_Articles'], merged_df['Copper_Price_USD'])

print("=== Copper Price vs. News 'Hype' Correlation Analysis ===")
print("Timeframe: 1 Year (Monthly Aggregation)")
print(f"Months analyzed: {len(merged_df)}\n")

print(merged_df.to_string(index=False))

print(f"\nPearson Correlation Coefficient (r): {corr_coef:.4f}")
print(f"P-value: {p_value:.4f}")

if p_value < 0.05:
    print("\nResult: There is a STATISTICALLY SIGNIFICANT correlation between premium news volume and copper price.")
    if corr_coef > 0:
        print("Interpretation: As copper prices rise, news coverage from premium outlets increases (or vice versa).")
    else:
         print("Interpretation: As copper prices rise, news coverage decreases.")
else:
    print("\nResult: NO statistically significant correlation was found between premium news volume and copper price.")
    print("Interpretation: The 'hype' from these specific outlets does not strictly track the price movements on a monthly basis based on this estimation method.")
    
# Save merged report
merged_df.to_csv("data/correlation_report_data.csv", index=False)
