# Daily AI Event Radar (每日 AI 事件雷达)

[English](#english) | [中文](#中文)

---

<h2 id="english">English</h2>

This repository contains scripts and a GitHub Actions workflow to run a daily scan for AI events, save the results, and generate reports.

### GitHub Actions Setup

A GitHub Actions workflow is included to automate the process of running the radar.

#### Workflow Details
- **Schedule**: The workflow is scheduled to run every day at 8:00 AM Pacific Time (`cron: '0 15 * * *'`).
- **Execution**: It installs dependencies from `requirements.txt` and runs `python main.py --days 30 --min-score 3`.
- **Artifacts**: The resulting output files (`outputs/events.csv`, `outputs/events.json`, `outputs/report.md`) are saved as downloadable artifacts on the workflow run.
- **Auto-Commit**: The workflow is configured to automatically commit the updated output files back to the repository.

#### Configuration Instructions

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

---

<h2 id="中文">中文</h2>

本项目包含相关脚本与 GitHub Actions 工作流，用于每日自动扫描 AI 事件，保存结果并生成报告。

### GitHub Actions 设置

项目中已包含 GitHub Actions 工作流，可实现雷达程序的自动化运行。

#### 工作流详情
- **定时计划**: 工作流会在每天太平洋时间上午 8:00 执行 (`cron: '0 15 * * *'`)。
- **执行过程**: 自动安装 `requirements.txt` 中的依赖，并运行 `python main.py --days 30 --min-score 3`。
- **运行产物**: 生成的输出文件（`outputs/events.csv`、`outputs/events.json` 和 `outputs/report.md`）将作为可下载的工作流产物（Artifacts）进行保存。
- **自动提交**: 工作流配置了自动提交功能，会将更新后的输出文件推送回代码库。

#### 配置说明

为确保工作流正常运行，请在您的代码库设置中进行以下配置：

1. **API 密钥 (Secrets)**:
   - 进入您的 GitHub 代码库主页。
   - 导航至 **Settings (设置)** > **Secrets and variables (密钥与变量)** > **Actions**。
   - 点击 **New repository secret (新建代码库密钥)**。
   - 添加您所需的 API 密钥（例如 `API_KEY`），以便工作流能够调用外部服务进行身份验证。请确保密钥名称与 `.github/workflows/daily_radar.yml` 文件中调用的名称一致。

2. **工作流权限 (Workflow Permissions)**:
   - 导航至 **Settings (设置)** > **Actions** > **General (常规)**。
   - 向下滚动至 **Workflow permissions (工作流权限)** 部分。
   - 选择 **Read and write permissions (读写权限)** 并保存。**这一步至关重要**，若未开启此权限，GitHub Action 将无法将新的 `outputs/` 文件提交回代码库。
