#!/usr/bin/env python3
"""
Test all platform integrations with enhanced Discord images
"""
import os
import requests
import json
from datetime import datetime

def test_all_platforms():
    """Test posting to Discord, Telegram, and Slack with images"""
    
    # Test product with high-quality image
    test_product = {
        'title': '🚀 AffiliateBot Pro - Live Test!',
        'description': 'Your automated affiliate marketing system is working perfectly! This is a test post with enhanced features.',
        'price': '$29.99',
        'rating': 4.9,
        'category': 'Marketing Tools',
        'affiliate_url': 'https://amazon.com/dp/TEST123?tag=luxoraconnect-20',
        'image_url': 'https://images-na.ssl-images-amazon.com/images/I/61vTzl8HbqL._AC_SL1500_.jpg'
    }
    
    print("🧪 Testing all your platforms...")
    
    # Test Discord with enhanced embed and image
    discord_url = os.environ.get('DISCORD_WEBHOOK_URL')
    if discord_url:
        test_discord_enhanced(discord_url, test_product)
    else:
        print("❌ Discord webhook URL not found")
    
    # Test Telegram
    telegram_token = os.environ.get('TELEGRAM_BOT_TOKEN')
    telegram_chat = os.environ.get('TELEGRAM_CHAT_ID')
    if telegram_token and telegram_chat:
        test_telegram(telegram_token, telegram_chat, test_product)
    else:
        print("❌ Telegram credentials not found")
    
    # Test Slack
    slack_token = os.environ.get('SLACK_BOT_TOKEN')
    slack_channel = os.environ.get('SLACK_CHANNEL_ID')
    if slack_token and slack_channel:
        test_slack(slack_token, slack_channel, test_product)
    else:
        print("❌ Slack credentials not found")

def test_discord_enhanced(webhook_url, product):
    """Enhanced Discord posting with better images and formatting"""
    print(f"\n🔷 Testing Discord with enhanced images...")
    
    embed = {
        "title": f"{product['title']}",
        "description": f"**{product['description']}**\n\n💰 **Price:** {product['price']}\n⭐ **Rating:** {product['rating']}/5\n📦 **Category:** {product['category']}\n\n🛒 **[GET IT NOW - Click Here!]({product['affiliate_url']})**",
        "url": product['affiliate_url'],
        "color": 0x00ff88,  # Green color
        "timestamp": datetime.now().isoformat(),
        "image": {"url": product['image_url']},  # Main large image
        "thumbnail": {"url": "https://cdn-icons-png.flaticon.com/512/2331/2331970.png"},  # Shopping cart icon
        "footer": {
            "text": "AffiliateBot Pro • Automated Affiliate Marketing",
            "icon_url": "https://cdn-icons-png.flaticon.com/512/3721/3721679.png"
        },
        "author": {
            "name": "🛍️ New Deal Alert!",
            "icon_url": "https://cdn-icons-png.flaticon.com/512/2331/2331970.png"
        }
    }
    
    payload = {
        "content": "🔥 **HOT DEAL ALERT!** 🔥",
        "embeds": [embed]
    }
    
    try:
        response = requests.post(webhook_url, json=payload, timeout=30)
        if response.status_code == 204:
            print("✅ Discord enhanced post successful!")
        else:
            print(f"❌ Discord error: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ Discord exception: {e}")

def test_telegram(bot_token, chat_id, product):
    """Test Telegram posting with photo"""
    print(f"\n📱 Testing Telegram...")
    
    caption = f"""🛍️ **{product['title']}**

{product['description']}

💰 Price: {product['price']}
⭐ Rating: {product['rating']}/5
📦 Category: {product['category']}

🛒 [GET IT NOW!]({product['affiliate_url']})

#affiliate #deals #amazon"""
    
    # Send photo with caption
    url = f"https://api.telegram.org/bot{bot_token}/sendPhoto"
    payload = {
        'chat_id': chat_id,
        'photo': product['image_url'],
        'caption': caption,
        'parse_mode': 'Markdown'
    }
    
    try:
        response = requests.post(url, json=payload, timeout=30)
        if response.status_code == 200:
            result = response.json()
            if result.get('ok'):
                print("✅ Telegram post successful!")
            else:
                print(f"❌ Telegram API error: {result}")
        else:
            print(f"❌ Telegram HTTP error: {response.status_code}")
    except Exception as e:
        print(f"❌ Telegram exception: {e}")

def test_slack(bot_token, channel_id, product):
    """Test Slack posting with image"""
    print(f"\n💬 Testing Slack...")
    
    headers = {
        'Authorization': f'Bearer {bot_token}',
        'Content-Type': 'application/json'
    }
    
    # Create rich message with image
    blocks = [
        {
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": f"🛍️ {product['title']}"
            }
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"*{product['description']}*\n\n💰 *Price:* {product['price']}\n⭐ *Rating:* {product['rating']}/5\n📦 *Category:* {product['category']}"
            },
            "accessory": {
                "type": "image",
                "image_url": product['image_url'],
                "alt_text": product['title']
            }
        },
        {
            "type": "actions",
            "elements": [
                {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "text": "🛒 GET IT NOW!"
                    },
                    "url": product['affiliate_url'],
                    "style": "primary"
                }
            ]
        }
    ]
    
    payload = {
        'channel': channel_id,
        'blocks': blocks,
        'text': f"New deal: {product['title']}"  # Fallback text
    }
    
    try:
        response = requests.post(
            'https://slack.com/api/chat.postMessage',
            headers=headers,
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get('ok'):
                print("✅ Slack post successful!")
            else:
                print(f"❌ Slack API error: {result.get('error')}")
        else:
            print(f"❌ Slack HTTP error: {response.status_code}")
    except Exception as e:
        print(f"❌ Slack exception: {e}")

if __name__ == "__main__":
    test_all_platforms()