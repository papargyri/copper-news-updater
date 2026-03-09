# 🤖 GitHub Actions Automation Strategy

To achieve robust daily updates of the copper news summary report, the recommended implementation is to move the fetching script into a GitHub repository and use GitHub Actions for scheduling.

## 🚀 Strategy: GitHub Actions + Webpage (Option 1)

This method removes reliance on a local computer and provides a versioned, beautifully rendered Markdown report on the GitHub website.

### 1. Repository Structure
The repository should contain:
- `copper_news_updater.py`: The Python script.
- `requirements.txt`: Python dependencies (`feedparser`, `requests`).
- `copper_news_summary.md`: The report file (updated automatically).
- `.github/workflows/update_news.yml`: The GitHub Actions configuration file.

### 2. GitHub Action Workflow Detail
The workflow file (`.github/workflows/update_news.yml`) should contain the following instructions:

```yaml
name: Daily Copper News Update

on:
  schedule:
    # Runs at 06:00 UTC every day.
    - cron: '0 6 * * *'
  # Allows you to manually trigger the workflow from the Actions tab
  workflow_dispatch:

jobs:
  update-news:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout repository
        uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.10'

      - name: Install dependencies
        run: pip install -r requirements.txt

      - name: Run script
        run: python copper_news_updater.py

      - name: Commit and push if changed
        run: |
          git config --global user.email "github-actions[bot]@users.noreply.github.com"
          git config --global user.name "github-actions[bot]"
          git add -A
          git diff --quiet && git diff --staged --quiet || git commit -m "chore: Update copper news summary"
          git push
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

**Note**: Granting write access to the repository is required so the script can commit the updated summary back to the `main` branch. This is configured in GitHub repository Settings > Actions > General > Workflow permissions.

### 3. Benefits of GitHub Actions
- **Reliability**: Updates occur on GitHub's servers, independent of the user's computer status (asleep, off, or disconnected).
- **History**: Every daily update creates a new commit, providing an exhaustive history of the market research progress.
- **Rendering**: GitHub automatically renders the `copper_news_summary.md` report as a clean, easy-to-read webpage.

---

## 🛠️ Implementation Steps Summary
1.  Initialize a local git repository in the project folder.
2.  Add and commit the script, dependencies, and report.
3.  Create the `.github/workflows/update_news.yml` file.
4.  Link the local repository to a remote GitHub repository.
5.  Push all changes to GitHub to activate the automation.
