import requests
import json
import logging
import os
from datetime import datetime

logger = logging.getLogger(__name__)

class MultiPlatformPoster:
    def __init__(self, user):
        self.user = user
        self.timeout = 30
        
        # Use environment secrets as primary, user settings as fallback
        self.discord_webhook_url = os.environ.get('DISCORD_WEBHOOK_URL') or user.discord_webhook_url
        self.telegram_bot_token = os.environ.get('TELEGRAM_BOT_TOKEN') or user.telegram_bot_token
        self.telegram_chat_id = os.environ.get('TELEGRAM_CHAT_ID') or user.telegram_chat_id
        self.slack_bot_token = os.environ.get('SLACK_BOT_TOKEN') or user.slack_bot_token
        self.slack_channel_id = os.environ.get('SLACK_CHANNEL_ID') or user.slack_channel_id
    
    def post_to_discord(self, product):
        """Post product to Discord webhook."""
        if not self.discord_webhook_url:
            return False
        
        embed = {
            "title": f"🛍️ {product['title']}",
            "description": product['description'],
            "url": product['affiliate_url'],
            "image": {"url": product['image']},
            "color": 3447003,
            "timestamp": datetime.now().isoformat(),
            "fields": [
                {"name": "💰 Price", "value": product['price'], "inline": True},
                {"name": "⭐ Rating", "value": f"{product['rating']}/5", "inline": True},
                {"name": "📦 Category", "value": product['category'], "inline": True}
            ],
            "footer": {"text": "Amazon Affiliate Bot"}
        }
        
        payload = {"embeds": [embed]}
        
        try:
            response = requests.post(self.user.discord_webhook_url, json=payload, timeout=self.timeout)
            if response.status_code == 204:
                logger.info("✅ Posted to Discord")
                return True
            else:
                logger.error(f"Discord error: {response.status_code}")
                return False
        except Exception as e:
            logger.error(f"Discord posting failed: {e}")
            return False

    def post_to_telegram(self, product):
        """Post product to Telegram."""
        if not self.telegram_bot_token or not self.telegram_chat_id:
            return False
        
        message = f"""🛍️ *{product['title']}*

{product['description']}

💰 Price: {product['price']}
⭐ Rating: {product['rating']}/5
📦 Category: {product['category']}

[🛒 Buy Now]({product['affiliate_url']})"""
        
        url = f"https://api.telegram.org/bot{self.user.telegram_bot_token}/sendMessage"
        payload = {
            "chat_id": self.user.telegram_chat_id,
            "text": message,
            "parse_mode": "Markdown",
            "disable_web_page_preview": False
        }
        
        try:
            response = requests.post(url, json=payload, timeout=self.timeout)
            if response.status_code == 200:
                logger.info("✅ Posted to Telegram")
                return True
            else:
                logger.error(f"Telegram error: {response.status_code}")
                return False
        except Exception as e:
            logger.error(f"Telegram posting failed: {e}")
            return False

    def post_to_slack(self, product):
        """Post product to Slack."""
        if not self.slack_bot_token or not self.slack_channel_id:
            return False
        
        try:
            from slack_sdk import WebClient
            from slack_sdk.errors import SlackApiError
            
            client = WebClient(token=self.slack_bot_token)
            
            blocks = [
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*🛍️ {product['title']}*\n{product['description']}"
                    },
                    "accessory": {
                        "type": "image",
                        "image_url": product["image"],
                        "alt_text": product["title"]
                    }
                },
                {
                    "type": "section",
                    "fields": [
                        {"type": "mrkdwn", "text": f"*💰 Price:*\n{product['price']}"},
                        {"type": "mrkdwn", "text": f"*⭐ Rating:*\n{product['rating']}/5"},
                        {"type": "mrkdwn", "text": f"*📦 Category:*\n{product['category']}"}
                    ]
                },
                {
                    "type": "actions",
                    "elements": [
                        {
                            "type": "button",
                            "text": {"type": "plain_text", "text": "🛒 Buy Now"},
                            "url": product["affiliate_url"],
                            "style": "primary"
                        }
                    ]
                }
            ]
            
            response = client.chat_postMessage(
                channel=self.slack_channel_id,
                blocks=blocks,
                text=f"New product: {product['title']}"
            )
            
            if response["ok"]:
                logger.info("✅ Posted to Slack")
                return True
            else:
                logger.error(f"Slack error: {response['error']}")
                return False
                
        except ImportError:
            logger.error("Slack SDK not installed")
            return False
        except Exception as e:
            logger.error(f"Slack posting failed: {e}")
            return False

    def send_email(self, product):
        """Send product email."""
        if not self.user.sendgrid_api_key or not self.user.email_from or not self.user.email_to:
            return False
        
        try:
            from sendgrid import SendGridAPIClient
            from sendgrid.helpers.mail import Mail
            
            html_content = f"""
            <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                <h2 style="color: #333;">🛍️ {product['title']}</h2>
                <img src="{product['image']}" alt="{product['title']}" style="max-width: 300px; height: auto; border-radius: 8px;">
                
                <p style="font-size: 16px; color: #555; line-height: 1.6;">{product['description']}</p>
                
                <div style="background: #f8f9fa; padding: 20px; border-radius: 8px; margin: 20px 0;">
                    <p><strong>💰 Price:</strong> {product['price']}</p>
                    <p><strong>⭐ Rating:</strong> {product['rating']}/5</p>
                    <p><strong>📦 Category:</strong> {product['category']}</p>
                </div>
                
                <a href="{product['affiliate_url']}" 
                   style="display: inline-block; background-color: #ff9900; color: white; 
                          padding: 15px 30px; text-decoration: none; border-radius: 5px; 
                          font-weight: bold; font-size: 16px;">
                    🛒 Buy Now on Amazon
                </a>
                
                <p style="margin-top: 30px; font-size: 12px; color: #888;">
                    This is an affiliate link. We may earn a commission from qualifying purchases.
                </p>
            </div>
            """
            
            message = Mail(
                from_email=self.user.email_from,
                to_emails=self.user.email_to,
                subject=f"🛍️ Amazing Deal: {product['title']}",
                html_content=html_content
            )
            
            sg = SendGridAPIClient(self.user.sendgrid_api_key)
            response = sg.send(message)
            
            if response.status_code == 202:
                logger.info("✅ Email sent")
                return True
            else:
                logger.error(f"Email error: {response.status_code}")
                return False
                
        except ImportError:
            logger.error("SendGrid not installed")
            return False
        except Exception as e:
            logger.error(f"Email sending failed: {e}")
            return False

    def post_product(self, product):
        """Post a product to all configured platforms."""
        logger.info(f"🚀 Posting product: {product['title']}")
        
        results = {
            'discord': self.post_to_discord(product),
            'telegram': self.post_to_telegram(product),
            'slack': self.post_to_slack(product),
            'email': self.send_email(product)
        }
        
        successful_posts = sum(results.values())
        logger.info(f"📊 Posted to {successful_posts} platforms")
        
        return results