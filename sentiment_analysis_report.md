# 🧠 Copper News Sentiment vs. Price Correlation Analysis

This report calculates the statistical relationship between the **NLP sentiment** of copper news articles (is the news positive/bullish or negative/bearish?) vs. the copper price movements over the next 1 to 3 days.

## 1. Linear Correlations (Pearson)

A correlation of 1 means perfect positive correlation (positive news = price goes up), -1 means perfect negative correlation (positive news = price crashes).

### Signal: `daily_sentiment`
- **1 Day Later**: Correlation = 0.045 (p-value: 0.353)
- **2 Days Later**: Correlation = 0.075 (p-value: 0.121)
- **3 Days Later**: Correlation = 0.110 (p-value: 0.022)
  - *Statistically significant!*

### Signal: `sentiment_smooth`
- **1 Day Later**: Correlation = 0.082 (p-value: 0.090)
- **2 Days Later**: Correlation = 0.109 (p-value: 0.023)
  - *Statistically significant!*
- **3 Days Later**: Correlation = 0.112 (p-value: 0.020)
  - *Statistically significant!*

## 2. Bullish vs Bearish News Days Simulation

**Day Classifications:** Bullish (76), Bearish (14), Neutral (340)

### 1 Day Later Average Price Change
- **After highly POSITIVE news:** 0.34%
- **After highly NEGATIVE news:** -1.67%
- **After NEUTRAL news:** 0.13%
  - *Observation: Positive news precedes stronger performance than negative news (Intuitive!)*

### 2 Days Later Average Price Change
- **After highly POSITIVE news:** 0.39%
- **After highly NEGATIVE news:** -2.63%
- **After NEUTRAL news:** 0.28%
  - *Observation: Positive news precedes stronger performance than negative news (Intuitive!)*

### 3 Days Later Average Price Change
- **After highly POSITIVE news:** 0.63%
- **After highly NEGATIVE news:** -3.23%
- **After NEUTRAL news:** 0.39%
  - *Observation: Positive news precedes stronger performance than negative news (Intuitive!)*
