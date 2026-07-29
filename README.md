# 武汉天气 Telegram Bot

每天早上 7:30 自动推送武汉天气预报到 Telegram。

## 功能

- 🌤 每日天气预报（温度、天气状况）
- ⏰ 每天北京时间 07:30 自动推送
- 🤖 通过 GitHub Actions 运行，无需本地服务器

## 快速开始

### 1. Fork/克隆此仓库

### 2. 配置 Secrets

在 GitHub 仓库设置中添加以下 Secrets：

**Settings → Secrets and variables → Actions → New repository secret**

| Secret Name | 说明 | 示例 |
|------------|------|------|
| `BOT_TOKEN` | Telegram Bot Token | `123456789:ABCdefGHIjklMNOpqrsTUVwxyz` |
| `CHAT_ID` | 你的 Telegram Chat ID | `123456789` |

### 3. 启用 GitHub Actions

- 进入仓库的 **Actions** 标签页
- 如果被禁用，点击 "I understand my workflows, go ahead and enable them"

### 4. 测试运行

在 Actions 页面找到 "Daily Wuhan Weather" workflow，点击 **Run workflow** 手动触发测试。

## 技术栈

- Python 3.12
- Telegram Bot API
- wttr.in 天气API（免费，无需 API Key）
- GitHub Actions（定时任务）

## 自定义

修改 `.github/workflows/weather.yml` 中的 cron 表达式来更改推送时间：

```yaml
schedule:
  - cron: "30 23 * * *"  # UTC 23:30 = 北京时间 07:30
```

## License

MIT
