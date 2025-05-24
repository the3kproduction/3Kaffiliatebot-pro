# Product Marketing Automation Script

A Python automation script that randomly selects products from a JSON catalog and posts them to Zapier webhooks for automated marketing campaigns.

## Features

- 🎯 Random product selection from JSON catalog
- 🔗 Zapier webhook integration
- 🛡️ Comprehensive error handling
- 📝 Detailed logging and status reporting
- ⚙️ Environment variable configuration
- 🚀 Ready for scheduled deployment

## Quick Start

### 1. Setup Environment

1. Copy the environment template:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` and add your Zapier webhook URL:
   ```
   WEBHOOK_URL=https://hooks.zapier.com/hooks/catch/your-id/your-token
   ```

### 2. Install Dependencies

```bash
pip install requests python-dotenv
```

### 3. Run the Script

```bash
python main.py
```

## Multi-Platform Marketing

Your automation now posts to ALL major platforms:

- 🎮 **Discord** - Rich embeds with product images
- 📱 **Telegram** - Formatted messages with product links  
- 💬 **Slack** - Professional blocks with action buttons
- 📧 **Email** - HTML newsletters via SendGrid

## Deployment to Render

Ready for 24/7 automated deployment:

### 1. Push to GitHub
1. Create a new repository on GitHub
2. Push this project to your repository

### 2. Deploy on Render
1. Go to [Render.com](https://render.com) and sign up
2. Click "New" → "Cron Job"
3. Connect your GitHub repository
4. Render will automatically detect the `render.yaml` configuration
5. Add your platform credentials in environment variables
6. Deploy!

The script runs every 3 hours, posting random products to ALL your configured platforms.

### Render Configuration
- **Type**: Cron Job (scheduled automation)
- **Schedule**: Every 3 hours (`0 */3 * * *`)
- **Runtime**: Python
- **Command**: `python main.py`

## Platform Setup (Choose Your Favorites!)

### Discord (Easiest & FREE!)
1. Create a Discord server or use existing one
2. Go to Server Settings → Integrations → Webhooks
3. Create New Webhook, copy the URL
4. Add to `DISCORD_WEBHOOK_URL`

### Telegram (FREE)
1. Message @BotFather on Telegram
2. Create a new bot with `/newbot`
3. Get your bot token and chat ID
4. Add to `TELEGRAM_BOT_TOKEN` and `TELEGRAM_CHAT_ID`

### Slack (FREE)
1. Create a Slack app at api.slack.com
2. Get your bot token
3. Add to `SLACK_BOT_TOKEN` and `SLACK_CHANNEL_ID`

### Email via SendGrid (FREE tier)
1. Sign up at sendgrid.com
2. Get your API key
3. Add to `SENDGRID_API_KEY`, `EMAIL_FROM`, `EMAIL_TO`

## Environment Variables

Set these in Render's dashboard (you only need the platforms you want):

| Variable | Platform | Required |
|----------|----------|----------|
| `DISCORD_WEBHOOK_URL` | Discord | For Discord posting |
| `TELEGRAM_BOT_TOKEN` | Telegram | For Telegram posting |
| `TELEGRAM_CHAT_ID` | Telegram | For Telegram posting |
| `SLACK_BOT_TOKEN` | Slack | For Slack posting |
| `SLACK_CHANNEL_ID` | Slack | For Slack posting |
| `SENDGRID_API_KEY` | Email | For email marketing |
| `EMAIL_FROM` | Email | Sender email address |
| `EMAIL_TO` | Email | Recipient email address |
