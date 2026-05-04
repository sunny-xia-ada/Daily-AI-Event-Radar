# Daily AI Event Radar (每日 AI 事件雷达)

[English](#english) | [中文](#中文)

---

<h2 id="english">English</h2>

This repository contains scripts and a GitHub Actions workflow to run a daily scan for AI events, save the results, and generate reports.

### GitHub Actions Setup

A GitHub Actions workflow is included to automate the process of running the radar.

#### Workflow Details
- **Schedule**: The workflow is scheduled to run using `cron: '0 15 * * *'`. This runs at 15:00 UTC. 
  - During **Daylight Saving Time**, this equals 8:00 AM Pacific Time.
  - During **Pacific Standard Time**, this equals 7:00 AM Pacific Time.
  - *Note: If you want exactly 8:00 AM PT year-round, you may need to update the cron seasonally or implement timezone-aware scheduling another way.*
- **Manual Trigger**: You can also trigger this workflow manually using the `workflow_dispatch` event in the GitHub Actions UI.
- **Execution**: It installs dependencies from `requirements.txt` and runs `python main.py --days 30 --min-score 3`.
- **Artifacts**: The resulting output files (`outputs/events.csv`, `outputs/events.json`, `outputs/report.md`) are saved as downloadable artifacts on the workflow run.
- **Auto-Commit**: The workflow is configured to automatically commit the updated output files back to the repository.

#### Configuration Instructions

To ensure the workflow runs correctly, you need to configure the following in your repository settings:

1. **API Keys (Secrets)**:
   - Go to your repository on GitHub.
   - Navigate to **Settings** > **Secrets and variables** > **Actions**.
   - Click **New repository secret**.
   - Add the specific keys used by the code:
     - `OPENAI_API_KEY`: Used for semantic relevance scoring.
     - `MEETUP_API_KEY`: Used to fetch Meetup events.
     - `EVENTBRITE_API_KEY`: Used to fetch Eventbrite events.
     - `TAVILY_API_KEY`: Used for web search.

2. **Workflow Permissions**:
   - Go to **Settings** > **Actions** > **General**.
   - Scroll down to the **Workflow permissions** section.
   - Select **Read and write permissions** and save. This step is crucial; without it, the GitHub Action will not be able to commit the new `outputs/` files back to the repository.

### Running Locally

1. Create a virtual environment and install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Copy the `.env.example` file to `.env` and fill in your API keys:
   ```bash
   cp .env.example .env
   ```
3. Run the script:
   ```bash
   python main.py --days 30 --min-score 3
   ```
   *(You can also use `--source luma` to run a specific source).*

### Testing

This project uses `pytest` for unit testing. To run the tests (which verify deduplication, title normalization, and fallback scoring):
```bash
pytest
```

---

<h2 id="中文">中文</h2>

本项目包含相关脚本与 GitHub Actions 工作流，用于每日自动扫描 AI 事件，保存结果并生成报告。

### GitHub Actions 设置

项目中已包含 GitHub Actions 工作流，可实现雷达的自动化运行。

#### 工作流详情
- **定时计划**: 工作流通过 `cron: '0 15 * * *'` 执行。对应时间为 15:00 UTC。
  - 在 **夏令时** 期间，这等于太平洋时间上午 8:00。
  - 在 **太平洋标准时间** 期间，这等于太平洋时间上午 7:00。
  - *注意：如果您希望全年都在精确的太平洋时间上午 8:00 运行，您可能需要随季节更新 cron 或通过其他方式实现带时区的调度。*
- **手动触发**: 您可以在 GitHub Actions 界面上使用 `workflow_dispatch` 手动触发此工作流。
- **执行过程**: 自动安装 `requirements.txt` 中的依赖，并运行 `python main.py --days 30 --min-score 3`。
- **运行产物**: 生成的输出文件（`outputs/events.csv`、`outputs/events.json` 和 `outputs/report.md`）将作为可下载的工作流产物（Artifacts）进行保存。
- **自动提交**: 工作流配置了自动提交功能，会将更新后的输出文件推送回代码库。

#### 配置说明

为确保工作流正常运行，请在您的代码库设置中进行以下配置：

1. **API 密钥 (Secrets)**:
   - 进入您的 GitHub 代码库主页。
   - 导航至 **Settings (设置)** > **Secrets and variables (密钥与变量)** > **Actions**。
   - 点击 **New repository secret (新建代码库密钥)**。
   - 根据代码所需，添加以下具体密钥：
     - `OPENAI_API_KEY`: 用于相关性的语义评分。
     - `MEETUP_API_KEY`: 用于获取 Meetup 活动。
     - `EVENTBRITE_API_KEY`: 用于获取 Eventbrite 活动。
     - `TAVILY_API_KEY`: 用于进行网页搜索。

2. **工作流权限 (Workflow Permissions)**:
   - 导航至 **Settings (设置)** > **Actions** > **General (常规)**。
   - 向下滚动至 **Workflow permissions (工作流权限)** 部分。
   - 选择 **Read and write permissions (读写权限)** 并保存。**这一步至关重要**，若未开启此权限，GitHub Action 将无法将新的 `outputs/` 文件提交回代码库。

### 本地运行

1. 创建虚拟环境并安装依赖：
   ```bash
   pip install -r requirements.txt
   ```
2. 将 `.env.example` 文件复制为 `.env` 并填写您的 API 密钥：
   ```bash
   cp .env.example .env
   ```
3. 运行脚本：
   ```bash
   python main.py --days 30 --min-score 3
   ```
   *（您也可以使用 `--source luma` 来运行指定数据源）。*

### 测试

本项目使用 `pytest` 进行单元测试。要运行测试（它们验证了去重、标题规范化和后备评分）：
```bash
pytest
```
