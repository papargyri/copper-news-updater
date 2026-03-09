# Copper Market News and Update Automation (Sept 2025 - Feb 2026)

This Knowledge Item summarizes research and implementation for tracking copper market trends and automating news updates.

## 📁 Artifacts

- **[copper_news_summary_2025_2026.md](./copper_news_summary_2025_2026.md)**: A high-level market report on demand (AI surge), supply shocks (Grasberg mine), and record prices.
- **[journalists_and_sources.md](./journalists_and_sources.md)**: A directory of key journalists (Harry Dempsey, Javier Blas, etc.) and primary news sources for the copper market.
- **[news_fetching_automation.md](./news_fetching_automation.md)**: Research on programmatic news fetching from premium outlets using RSS and APIs.
- **[docs/copper_news_updater_script.md](./docs/copper_news_updater_script.md)**: The Python script logic for fetching and appending news to a Markdown summary.
- **[docs/github_actions_workflow.md](./docs/github_actions_workflow.md)**: Detailed strategy for automating updates using GitHub Actions.

## 🚀 Key Insights

- **Demand Shift**: The primary catalyst for the 2026 price surge was **AI Data Center** infrastructure, colliding with existing green energy trends (EVs, power grids).
- **Supply Fragility**: The market transitioned from surplus to structural deficit following major disruptions like the **Grasberg mine mudslide**.
- **Automation Philosophy**: Moving from local `cron` jobs to **GitHub Actions** provides the most robust, "set-it-and-forget-it" update mechanism for market research reports.
