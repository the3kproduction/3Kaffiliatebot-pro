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

## Deploy to Render (Ready for Production!)

Your platform is ready to deploy and start collecting user signups:

### 1. Push to GitHub
1. Create a new repository on GitHub
2. Push this entire project to your repository

### 2. Deploy on Render
1. Go to [Render.com](https://render.com) and sign up
2. Click "New" → "Blueprint"
3. Connect your GitHub repository
4. Render will automatically detect the `render.yaml` configuration
5. Add your SendGrid API key for email blasts (optional)
6. Deploy!

### 3. Make Yourself Admin
Once deployed, you'll need to make yourself an admin to access the money-making features:

1. Sign up on your live site using your email
2. Access your database and run: `UPDATE users SET is_admin = true WHERE email = 'your-email@domain.com';`
3. You'll now see the Admin panel in the navigation

## Money-Making Features

Once deployed, you'll have access to:

- **Admin Dashboard**: View all user signups and their emails
- **Email Blast System**: Send marketing campaigns to your entire user base
- **User Analytics**: Track signups, engagement, and revenue potential
- **Subscription Management**: Manage free/premium/pro tiers

## Environment Variables (All Optional)

| Variable | Purpose | Required |
|----------|---------|----------|
| `SESSION_SECRET` | Auto-generated | Automatic |
| `SENDGRID_API_KEY` | For admin email blasts | Optional |
| `EMAIL_FROM` | Email sender address | Optional |

## Revenue Streams

1. **Subscription Tiers**: Charge users for higher posting frequencies
2. **Email Marketing**: Blast promotional emails to your entire user base
3. **Affiliate Commissions**: Take a percentage of user earnings
4. **Course Sales**: Sell affiliate marketing courses to your users
5. **Premium Features**: Charge for advanced analytics and tools
