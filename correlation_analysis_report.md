# 📈 Copper News Volume vs. Price Correlation Analysis

This report calculates the statistical relationship between the volume of copper news articles (and their daily changes) today vs. the copper price movements over the next 1 to 3 days.

## 1. Linear Correlations (Pearson)

A correlation of 1 means perfect positive correlation, -1 means perfect negative correlation, and 0 means no correlation.

### Signal: `global_count`
- **1 Day Later**: Correlation = -0.077 (p-value: 0.111)
- **2 Days Later**: Correlation = -0.105 (p-value: 0.030)
  - *Statistically significant!*
- **3 Days Later**: Correlation = -0.106 (p-value: 0.028)
  - *Statistically significant!*

### Signal: `premium_count`
- **1 Day Later**: Correlation = -0.063 (p-value: 0.191)
- **2 Days Later**: Correlation = -0.147 (p-value: 0.002)
  - *Statistically significant!*
- **3 Days Later**: Correlation = -0.116 (p-value: 0.016)
  - *Statistically significant!*

### Signal: `global_change`
- **1 Day Later**: Correlation = -0.020 (p-value: 0.680)
- **2 Days Later**: Correlation = -0.043 (p-value: 0.374)
- **3 Days Later**: Correlation = -0.054 (p-value: 0.261)

### Signal: `premium_change`
- **1 Day Later**: Correlation = 0.065 (p-value: 0.180)
- **2 Days Later**: Correlation = -0.058 (p-value: 0.230)
- **3 Days Later**: Correlation = -0.020 (p-value: 0.676)

## 2. Spike Analysis (Event Study)

What happens to the price after a notable spike in news articles? Let's define a 'Spike' as a day where the `global_count` is in the top 20% of all days.

**Top 20% Threshold:** 6.0 articles (Spike days: 108, Normal days: 321)

### 1 Day Later Average Price Change
- **After a News Spike:** -0.01%
- **After Normal Days:** 0.14%
  - *Observation: High news volume tends to precede weaker price performance.*

### 2 Days Later Average Price Change
- **After a News Spike:** 0.05%
- **After Normal Days:** 0.25%
  - *Observation: High news volume tends to precede weaker price performance.*

### 3 Days Later Average Price Change
- **After a News Spike:** 0.03%
- **After Normal Days:** 0.40%
  - *Observation: High news volume tends to precede weaker price performance.*

## 3. Momentum Trading Simulation (Hypothetical)

If we bought copper when the `global_change` (day-over-day news increase) was highly positive, vs when it dropped, what would the T+2 return look like?

- **Average 2-Day Return when News Volume INCREASES (Positive Delta):** 0.17%
- **Average 2-Day Return when News Volume DECREASES (Negative Delta):** 0.23%