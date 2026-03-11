# Copper Market News and Update Automation (Sept 2025 - Feb 2026)

This repository contains scripts and documentation for tracking copper market trends and automating daily news updates.

## 📁 Artifacts

- **[copper_news_summary_2025_2026.md](./copper_news_summary_2025_2026.md)**: A high-level market report on demand (AI surge), supply shocks (Grasberg mine), and record prices.
- **[copper_price_analysis.md](./copper_price_analysis.md)**: A dedicated view parsing out the correlation between raw Copper Futures Prices vs Global News Volume. Includes an instantly rendering visual overview.
- **[news_fetching_automation.md](./news_fetching_automation.md)**: Research on programmatic news fetching from premium outlets using RSS and APIs.
- **[docs/copper_news_updater_script.md](./docs/copper_news_updater_script.md)**: The Python script logic for fetching and appending news to a Markdown summary.
- **[docs/github_actions_workflow.md](./docs/github_actions_workflow.md)**: Detailed strategy for automating updates using GitHub Actions.

> [!NOTE]
> **Viewing the Interactive Chart (`copper_analysis_chart.html`)**: If you want the version of the data view with toggles and zooming, download `copper_analysis_chart.html`. This file embeds necessary JavaScript libraries (such as Plotly) to function completely offline without internet dependencies. Because of its size (~5MB), GitHub's unified "View raw" screen may display a *"We can't show files that are this big right now"* message. **This is normal for GitHub.** To view the chart and interact with its toggles, click the **Download raw file** button on the top right corner of the file view on GitHub, and open the `.html` file locally in any web browser.

## 🚀 Key Insights

- **Demand Shift**: The primary catalyst for the 2026 price surge was **AI Data Center** infrastructure, colliding with existing green energy trends (EVs, power grids).
- **Supply Fragility**: The market transitioned from surplus to structural deficit following major disruptions like the **Grasberg mine mudslide**.
- **Automation Philosophy**: Moving from local `cron` jobs to **GitHub Actions** provides the most robust, "set-it-and-forget-it" update mechanism for market research reports.
