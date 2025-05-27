#!/usr/bin/env python3
"""
INSTANT PRODUCT PROMOTION - START EARNING NOW!
"""

import os
import requests

def promote_echo_dot():
    """Promote Amazon Echo Dot - High converting product!"""
    
    # Your affiliate link with tracking
    affiliate_url = "https://www.amazon.com/dp/B09B8V1LZ3?tag=luxoraconnect-20"
    
    # Proven high-converting message
    message = """🔥 DEAL ALERT! Amazon Echo Dot (5th Gen) 🔥

✨ Smart speaker with Alexa
💰 Price: $49.99 (Was $69.99!)
⭐ Rating: 4.7/5 stars - 85,000+ reviews

🛒 Get yours: """ + affiliate_url + """

Perfect for smart home control, music, and voice commands!
#AmazonDeals #SmartHome #TechDeals"""

    print("🚀 PROMOTING HIGH-CONVERTING PRODUCT...")
    print(f"🎯 Product: Amazon Echo Dot (5th Gen)")
    print(f"💰 Your commission: ~$2-4 per sale")
    
    success_count = 0
    
    # POST TO DISCORD
    discord_webhook = os.environ.get('DISCORD_WEBHOOK_URL')
    if discord_webhook:
        try:
            discord_data = {
                "content": "🚨 **AMAZING TECH DEAL!** 🚨",
                "embeds": [{
                    "title": "🔥 Amazon Echo Dot (5th Gen) - ON SALE!",
                    "description": f"💰 **Just $49.99** (Save $20!)\n⭐ **4.7/5 stars** - 85,000+ reviews\n\n🛒 [**GET IT NOW!**]({affiliate_url})",
                    "url": affiliate_url,
                    "image": {"url": "https://m.media-amazon.com/images/I/61SUj8zKlHL._AC_SL1000_.jpg"},
                    "color": 0x00ff00,
                    "footer": {"text": "🤖 Limited time deal - Act fast!"}
                }]
            }
            response = requests.post(discord_webhook, json=discord_data, timeout=10)
            if response.status_code == 204:
                print("✅ Posted to Discord!")
                success_count += 1
            else:
                print(f"❌ Discord failed: {response.status_code}")
        except Exception as e:
            print(f"❌ Discord error: {e}")
    
    # POST TO SLACK
    slack_token = os.environ.get('SLACK_BOT_TOKEN')
    slack_channel = os.environ.get('SLACK_CHANNEL_ID')
    if slack_token and slack_channel:
        try:
            slack_url = "https://slack.com/api/chat.postMessage"
            slack_headers = {"Authorization": f"Bearer {slack_token}"}
            slack_data = {
                "channel": slack_channel,
                "text": message,
                "attachments": [{
                    "color": "good",
                    "image_url": "https://m.media-amazon.com/images/I/61SUj8zKlHL._AC_SL1000_.jpg",
                    "title": "Amazon Echo Dot (5th Gen) - Limited Time Deal!",
                    "title_link": affiliate_url
                }]
            }
            response = requests.post(slack_url, headers=slack_headers, json=slack_data, timeout=10)
            if response.status_code == 200:
                print("✅ Posted to Slack!")
                success_count += 1
            else:
                print(f"❌ Slack failed: {response.status_code}")
        except Exception as e:
            print(f"❌ Slack error: {e}")
    
    # POST TO TELEGRAM
    telegram_token = os.environ.get('TELEGRAM_BOT_TOKEN')
    telegram_chat = os.environ.get('TELEGRAM_CHAT_ID')
    if telegram_token and telegram_chat:
        try:
            telegram_url = f"https://api.telegram.org/bot{telegram_token}/sendPhoto"
            telegram_data = {
                "chat_id": telegram_chat,
                "photo": "https://m.media-amazon.com/images/I/61SUj8zKlHL._AC_SL1000_.jpg",
                "caption": f"🔥 DEAL ALERT! Amazon Echo Dot (5th Gen)\n\n💰 Just $49.99 (Save $20!)\n⭐ 4.7/5 stars\n\n🛒 Get it: {affiliate_url}",
                "parse_mode": "Markdown"
            }
            response = requests.post(telegram_url, data=telegram_data, timeout=10)
            if response.status_code == 200:
                print("✅ Posted to Telegram!")
                success_count += 1
            else:
                print(f"❌ Telegram failed: {response.status_code}")
        except Exception as e:
            print(f"❌ Telegram error: {e}")
    
    if success_count > 0:
        print(f"\n🎉 SUCCESS! Posted to {success_count} platform(s)")
        print(f"💰 Your affiliate link is now live: {affiliate_url}")
        print(f"📈 Expected earnings: $2-4 per sale")
        print(f"🎯 This product converts at ~2-3% click rate")
    else:
        print("\n❌ No platforms posted successfully!")
        print("💡 Make sure you have these environment variables set:")
        print("   - DISCORD_WEBHOOK_URL")
        print("   - SLACK_BOT_TOKEN + SLACK_CHANNEL_ID")
        print("   - TELEGRAM_BOT_TOKEN + TELEGRAM_CHAT_ID")

if __name__ == "__main__":
    promote_echo_dot()