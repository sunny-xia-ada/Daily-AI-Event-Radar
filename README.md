# Daily AI Event Radar

This repository contains scripts and a GitHub Actions workflow to run a daily scan for AI events, save the results, and generate reports.

## GitHub Actions Setup

A GitHub Actions workflow is included to automate the process of running the radar.

### Workflow Details
- **Schedule**: The workflow is scheduled to run every day at 8:00 AM Pacific Time (`cron: '0 15 * * *'`).
- **Execution**: It installs dependencies from `requirements.txt` and runs `python main.py --days 30 --min-score 3`.
- **Artifacts**: The resulting output files (`outputs/events.csv`, `outputs/events.json`, `outputs/report.md`) are saved as downloadable artifacts on the workflow run.
- **Auto-Commit**: The workflow is configured to automatically commit the updated output files back to the repository.

### Configuration Instructions

To ensure the workflow runs correctly, you need to configure the following in your repository settings:

1. **API Keys (Secrets)**:
   - Go to your repository on GitHub.
   - Navigate to **Settings** > **Secrets and variables** > **Actions**.
   - Click **New repository secret**.
   - Add your required API keys (e.g., `API_KEY`) so the workflow can authenticate with external services. Ensure the names of the secrets match what is expected in `.github/workflows/daily_radar.yml`.

2. **Workflow Permissions**:
   - Go to **Settings** > **Actions** > **General**.
   - Scroll down to the **Workflow permissions** section.
   - Select **Read and write permissions** and save. This step is crucial; without it, the GitHub Action will not be able to commit the new `outputs/` files back to the repository.
