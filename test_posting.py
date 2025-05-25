#!/usr/bin/env python3
"""
Test posting functionality using credentials from user profile
"""
import os
import sys
import requests
import json
from datetime import datetime

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app, db
from models import User

def test_user_posting():
    """Test posting with user's saved credentials"""
    with app.app_context():
        # Get the admin user (your account)
        user = User.query.filter_by(email='drfe8694@gmail.com').first()
        
        if not user:
            print("❌ User not found")
            return
            
        print(f"✅ Found user: {user.email}")
        print(f"📊 Affiliate ID: {user.amazon_affiliate_id or 'Not set'}")
        print(f"🔗 Discord: {'✅ Configured' if user.discord_webhook_url else '❌ Not set'}")
        print(f"📱 Telegram: {'✅ Configured' if user.telegram_bot_token else '❌ Not set'}")
        print(f"💬 Slack: {'✅ Configured' if user.slack_bot_token else '❌ Not set'}")
        print(f"📧 Email: {'✅ Configured' if user.sendgrid_api_key else '❌ Not set'}")
        
        # Test product for posting
        test_product = {
            'title': 'AffiliateBot Pro Test Product 🚀',
            'description': 'Testing your automated affiliate posting system!',
            'price': '$29.99',
            'rating': 4.8,
            'category': 'Technology',
            'affiliate_url': f'https://amazon.com/dp/TEST123?tag={user.amazon_affiliate_id}',
            'image_url': 'https://via.placeholder.com/400x300/4CAF50/white?text=Test+Product'
        }
        
        # Test Slack posting if configured
        if user.slack_bot_token and user.slack_channel_id:
            try:
                test_slack_post(user, test_product)
            except Exception as e:
                print(f"❌ Slack test failed: {e}")
        
        # Test Discord posting if configured  
        if user.discord_webhook_url:
            try:
                test_discord_post(user, test_product)
            except Exception as e:
                print(f"❌ Discord test failed: {e}")
                
        print("\n🎉 Testing complete! Check your channels for test posts.")

def test_slack_post(user, product):
    """Test Slack posting"""
    print(f"\n🧪 Testing Slack post to #{user.slack_channel_id}...")
    
    headers = {
        'Authorization': f'Bearer {user.slack_bot_token}',
        'Content-Type': 'application/json'
    }
    
    message = f"""🛍️ **{product['title']}**
    
💰 Price: {product['price']}
⭐ Rating: {product['rating']}/5
📦 Category: {product['category']}

🛒 **GET IT NOW:** {product['affiliate_url']}

#affiliate #deals #amazon #social"""
    
    payload = {
        'channel': user.slack_channel_id,
        'text': message,
        'username': 'AffiliateBot Pro',
        'icon_emoji': ':robot_face:'
    }
    
    response = requests.post(
        'https://slack.com/api/chat.postMessage',
        headers=headers,
        json=payload,
        timeout=30
    )
    
    if response.status_code == 200:
        result = response.json()
        if result.get('ok'):
            print("✅ Slack test post successful!")
        else:
            print(f"❌ Slack API error: {result.get('error')}")
    else:
        print(f"❌ Slack HTTP error: {response.status_code}")

def test_discord_post(user, product):
    """Test Discord posting"""
    print(f"\n🧪 Testing Discord post...")
    
    embed = {
        "title": f"🛍️ {product['title']}",
        "description": product['description'],
        "url": product['affiliate_url'],
        "color": 3447003,
        "timestamp": datetime.now().isoformat(),
        "thumbnail": {"url": product['image_url']},
        "fields": [
            {"name": "💰 Price", "value": product['price'], "inline": True},
            {"name": "⭐ Rating", "value": f"{product['rating']}/5", "inline": True},
            {"name": "📦 Category", "value": product['category'], "inline": True}
        ],
        "footer": {"text": "AffiliateBot Pro"}
    }
    
    payload = {"embeds": [embed]}
    
    response = requests.post(
        user.discord_webhook_url,
        json=payload,
        timeout=30
    )
    
    if response.status_code == 204:
        print("✅ Discord test post successful!")
    else:
        print(f"❌ Discord HTTP error: {response.status_code}")

if __name__ == "__main__":
    test_user_posting()