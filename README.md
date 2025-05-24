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
