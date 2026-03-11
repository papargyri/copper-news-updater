# 🔮 Copper Price Predictive Mechanism: Feature Engineering & Architecture

To build a robust predictive mechanism (like a Machine Learning model) that forecasts copper prices, we cannot rely on news sentiment and volume alone. While our scripts proved they carry statistically significant signals, financial markets are highly complex multivariate systems. News is often a *lagging* or heavily *noisy* feature. 

To create a complete predictive model, we need to incorporate a blend of **Alternative Data (News)**, **Fundamental Data (Supply/Demand)**, **Macroeconomic Data**, and **Technical Data**.

## 1. Additional Features Required for Completeness

If we were to build a dataset for a predictive model (e.g., a Random Forest Classifier to predict "Up/Down", or an LSTM Neural Network to predict price), we should pull the following APIs to build our daily feature vector:

### A. Fundamental & Structural Data (The Reality of Supply/Demand)
News talks about supply and demand; these metrics *are* supply and demand.
- **LME (London Metal Exchange) & COMEX Copper Inventories:** The physical stockpile levels of copper in global warehouses. When inventories drop historically low, price spikes are imminent regardless of the news.
- **Commitments of Traders (COT) Report:** Weekly data showing the net long/short positions of hedge funds and institutional speculators on copper futures. This tells us what the "smart money" is actively doing.

### B. Macroeconomic Indicators (The Cost of Money)
Copper is often called "Doctor Copper" because it is a proxy for global economic health. Its price is directly tied to the US Dollar.
- **US Dollar Index (DXY):** Copper is priced in US Dollars globally. Usually, when the DXY goes *down*, Copper goes *up* (inverse correlation), and vice versa.
- **China Manufacturing PMI (Purchasing Managers' Index):** China consumes over 50% of the world's copper. Their monthly PMI data dictates global demand. If China's factories are expanding, copper demand rises.
- **Interest Rates / Yield Curve:** The cost of capital for infrastructure and EV projects.

### C. Enhanced Alternative Data (Deepening our existing work)
- **News Topic Modeling:** Instead of just "Positive/Negative", use NLP (like BERTopic or LDA) to categorize the *subject* of the article. Is it about "AI Data Centers", "EVs", "Mine Strikes in Chile", or "Tariffs"?
- **Source Weighting:** A bullish article from *Reuters* or *Bloomberg* carries more market-moving weight than an obscure local news site. We can weight the sentiment by the outlet's tier (Elite vs Global).

### D. Technical Market Indicators
Mathematical derivatives of the price itself to capture market momentum.
- **Moving Averages (e.g., 50-day and 200-day Simple Moving Average):** To determine the macro trend.
- **RSI (Relative Strength Index):** To identify if the asset is mathematically "overbought" (>70) or "oversold" (<30) at the time the news hits.

---

## 2. Proposed System Architecture

1. **Data Ingestion Pipeline:** 
   - A daily cron job (similar to our current news updater) that fetches the daily closing price of Copper, the DXY index, LME inventory levels, and scrapes the news articles.
2. **Feature Engineering Layer:** 
   - Calculates the 3-day rolling sentiment.
   - Calculates the RSI and Moving Average divergence.
   - Calculates day-over-day inventory change.
3. **The Machine Learning Model (XGBoost or Random Forest):**
   - We feed the engineered daily feature vector into a tree-based classification model.
   - **Target Variable (The Prediction):** Will the copper price close higher or lower in T+3 days? (Binary Classification: 1 for Up, 0 for Down).
4. **Validation (Backtesting):**
   - We train the model on data from Jan 2025 to Present.
   - We test the model's accuracy, specifically looking for precision on "Buy" signals to ensure it beats a simple buy-and-hold strategy.

By combining the **News Sentiment (Retail/Hype Catalyst)** with **LME Inventories (Physical Reality)** and the **DXY (Macro Reality)**, the predictive capability of the mechanism becomes vastly more complete and resilient.
