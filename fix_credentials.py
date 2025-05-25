#!/usr/bin/env python3
"""
Fix user credentials by copying from environment to user profile
"""
import os
from app import app, db
from models import User

def fix_user_credentials():
    """Copy environment credentials to user profile"""
    with app.app_context():
        # Get admin user
        user = User.query.filter_by(email='drfe8694@gmail.com').first()
        if not user:
            print("❌ User not found")
            return
        
        # Update user credentials from environment
        discord_webhook = os.environ.get('DISCORD_WEBHOOK_URL')
        telegram_token = os.environ.get('TELEGRAM_BOT_TOKEN')
        telegram_chat = os.environ.get('TELEGRAM_CHAT_ID')
        slack_token = os.environ.get('SLACK_BOT_TOKEN')
        slack_channel = os.environ.get('SLACK_CHANNEL_ID')
        
        # Update user profile
        if discord_webhook:
            user.discord_webhook_url = discord_webhook
            print("✅ Discord webhook updated")
        
        if telegram_token:
            user.telegram_bot_token = telegram_token
            print("✅ Telegram token updated")
            
        if telegram_chat:
            user.telegram_chat_id = telegram_chat
            print("✅ Telegram chat ID updated")
            
        if slack_token:
            user.slack_bot_token = slack_token
            print("✅ Slack token updated")
            
        if slack_channel:
            user.slack_channel_id = slack_channel
            print("✅ Slack channel updated")
        
        # Commit changes
        db.session.commit()
        
        print(f"\n🎉 Updated credentials for {user.email}")
        print(f"✅ Discord: {'Configured' if user.discord_webhook_url else 'Not set'}")
        print(f"✅ Telegram: {'Configured' if user.telegram_bot_token else 'Not set'}")
        print(f"✅ Slack: {'Configured' if user.slack_bot_token else 'Not set'}")

if __name__ == "__main__":
    fix_user_credentials()