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

## Deployment to Render

This project is ready for 24/7 automated deployment on Render:

### 1. Push to GitHub
1. Create a new repository on GitHub
2. Push this project to your repository

### 2. Deploy on Render
1. Go to [Render.com](https://render.com) and sign up
2. Click "New" → "Cron Job"
3. Connect your GitHub repository
4. Render will automatically detect the `render.yaml` configuration
5. Set your `WEBHOOK_URL` environment variable in the Render dashboard
6. Deploy!

The script will run automatically every 3 hours, posting random products to your Zapier webhook.

### Render Configuration
- **Type**: Cron Job (runs on schedule)
- **Schedule**: Every 3 hours (`0 */3 * * *`)
- **Runtime**: Python
- **Command**: `python main.py`

## Environment Variables

You need to set these in Render's dashboard:

| Variable | Description | Example |
|----------|-------------|---------|
| `WEBHOOK_URL` | Your Zapier webhook URL | `https://hooks.zapier.com/hooks/catch/123/abc` |
