#!/usr/bin/env python3
"""
Quick test to check platform posting
"""
import requests
import json
from models import User
from app import app, db

def test_discord_webhook():
    """Test Discord webhook posting"""
    with app.app_context():
        user = User.query.first()
        if not user or not user.discord_webhook_url:
            print("❌ No Discord webhook configured")
            return False
        
        test_payload = {
            "embeds": [{
                "title": "🛍️ Test Product",
                "description": "Testing Discord webhook connection",
                "color": 3447003,
                "fields": [
                    {"name": "💰 Price", "value": "$29.99", "inline": True},
                    {"name": "⭐ Rating", "value": "4.5/5", "inline": True}
                ]
            }]
        }
        
        try:
            response = requests.post(
                user.discord_webhook_url,
                json=test_payload,
                timeout=10
            )
            
            if response.status_code == 204:
                print("✅ Discord webhook working!")
                return True
            else:
                print(f"❌ Discord webhook failed: {response.status_code}")
                print(f"Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Discord webhook error: {e}")
            return False

def test_telegram_bot():
    """Test Telegram bot posting"""
    with app.app_context():
        user = User.query.first()
        if not user or not user.telegram_bot_token or not user.telegram_chat_id:
            print("❌ No Telegram bot configured")
            return False
        
        url = f"https://api.telegram.org/bot{user.telegram_bot_token}/sendMessage"
        
        test_payload = {
            "chat_id": user.telegram_chat_id,
            "text": "🛍️ *Test Product*\n\nTesting Telegram bot connection\n\n💰 Price: $29.99\n⭐ Rating: 4.5/5",
            "parse_mode": "Markdown"
        }
        
        try:
            response = requests.post(url, json=test_payload, timeout=10)
            
            if response.status_code == 200:
                print("✅ Telegram bot working!")
                return True
            else:
                print(f"❌ Telegram bot failed: {response.status_code}")
                print(f"Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Telegram bot error: {e}")
            return False

if __name__ == "__main__":
    print("🧪 Testing platform connections...")
    print()
    
    discord_ok = test_discord_webhook()
    telegram_ok = test_telegram_bot()
    
    print()
    if discord_ok or telegram_ok:
        print("✅ At least one platform is working!")
    else:
        print("❌ All platforms failed - need to check configurations")