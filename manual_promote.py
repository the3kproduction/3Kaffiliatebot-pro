#!/usr/bin/env python3
"""
Quick Manual Product Promotion Script
Run this to instantly promote a product to all your connected platforms!
"""

import os
import sys
import requests
from working_app import app
from models import ProductInventory

def promote_product_now(asin=None):
    """Promote a product immediately to all connected platforms"""
    
    with app.app_context():
        # Get a product to promote
        if asin:
            product = ProductInventory.query.filter_by(asin=asin).first()
        else:
            # Get highest rated product
            product = ProductInventory.query.filter(
                ProductInventory.rating >= 4.0
            ).order_by(ProductInventory.rating.desc()).first()
        
        if not product:
            print("❌ No products found!")
            return
        
        # Create affiliate URL
        affiliate_id = "luxoraconnect-20"
        affiliate_url = f"https://www.amazon.com/dp/{product.asin}?tag={affiliate_id}"
        
        # Format message
        message = f"""🔥 AMAZING DEAL ALERT! 🔥

✨ {product.product_title}
💰 Price: {product.price}
⭐ Rating: {product.rating}/5 stars

🛒 Get yours here: {affiliate_url}

Don't miss out on this incredible deal!
#AmazonDeals #TechDeals #Shopping"""

        print(f"🚀 Promoting: {product.product_title}")
        print(f"🔗 Affiliate URL: {affiliate_url}")
        
        platforms_posted = []
        
        # POST TO DISCORD
        discord_webhook = os.environ.get('DISCORD_WEBHOOK_URL')
        if discord_webhook:
            try:
                discord_data = {
                    "content": "🚨 **HOT DEAL ALERT!** 🚨",
                    "embeds": [{
                        "title": f"🔥 {product.product_title}",
                        "description": f"💰 **Price:** {product.price}\n⭐ **Rating:** {product.rating}/5 stars\n\n🛒 [**GET IT NOW!**]({affiliate_url})",
                        "url": affiliate_url,
                        "image": {"url": product.image_url} if product.image_url else None,
                        "color": 0x00ff00,
                        "footer": {"text": "🤖 Posted by AffiliateBot Pro"}
                    }]
                }
                response = requests.post(discord_webhook, json=discord_data, timeout=10)
                if response.status_code == 204:
                    platforms_posted.append("Discord")
                    print("✅ Posted to Discord!")
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
                        "image_url": product.image_url,
                        "title": product.product_title,
                        "title_link": affiliate_url
                    }]
                }
                response = requests.post(slack_url, headers=slack_headers, json=slack_data, timeout=10)
                if response.status_code == 200 and response.json().get("ok"):
                    platforms_posted.append("Slack")
                    print("✅ Posted to Slack!")
                else:
                    print(f"❌ Slack failed: {response.status_code}")
            except Exception as e:
                print(f"❌ Slack error: {e}")
        
        # POST TO TELEGRAM
        telegram_token = os.environ.get('TELEGRAM_BOT_TOKEN')
        telegram_chat = os.environ.get('TELEGRAM_CHAT_ID')
        if telegram_token and telegram_chat:
            try:
                telegram_url = f"https://api.telegram.org/bot{telegram_token}/sendMessage"
                telegram_data = {
                    "chat_id": telegram_chat,
                    "text": message,
                    "parse_mode": "Markdown",
                    "disable_web_page_preview": False
                }
                response = requests.post(telegram_url, json=telegram_data, timeout=10)
                if response.status_code == 200:
                    platforms_posted.append("Telegram")
                    print("✅ Posted to Telegram!")
                else:
                    print(f"❌ Telegram failed: {response.status_code}")
            except Exception as e:
                print(f"❌ Telegram error: {e}")
        
        if platforms_posted:
            print(f"\n🎉 SUCCESS! Posted to: {', '.join(platforms_posted)}")
            print(f"💰 Start earning commissions from: {affiliate_url}")
        else:
            print("\n❌ No platforms configured or all failed!")
            print("💡 Set up your platform credentials in environment variables:")
            print("   - DISCORD_WEBHOOK_URL")
            print("   - SLACK_BOT_TOKEN + SLACK_CHANNEL_ID") 
            print("   - TELEGRAM_BOT_TOKEN + TELEGRAM_CHAT_ID")

if __name__ == "__main__":
    # Get ASIN from command line if provided
    asin = sys.argv[1] if len(sys.argv) > 1 else None
    promote_product_now(asin)