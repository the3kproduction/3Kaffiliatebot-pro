#!/usr/bin/env python3
"""
Multi-Platform Product Marketing Automation Script

This script randomly selects products from a JSON catalog and posts them
to multiple social media and marketing platforms automatically.
"""

import requests
import json
import random
import os
import sys
import logging
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

# Configuration
PRODUCTS_FILE = "products.json"
REQUEST_TIMEOUT = 30  # seconds

# Platform API Configuration
TWITTER_BEARER_TOKEN = os.getenv("TWITTER_BEARER_TOKEN")
FACEBOOK_ACCESS_TOKEN = os.getenv("FACEBOOK_ACCESS_TOKEN")
FACEBOOK_PAGE_ID = os.getenv("FACEBOOK_PAGE_ID")
DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")
SLACK_BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN")
SLACK_CHANNEL_ID = os.getenv("SLACK_CHANNEL_ID")
SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY")
EMAIL_FROM = os.getenv("EMAIL_FROM")
EMAIL_TO = os.getenv("EMAIL_TO")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

def validate_environment():
    """Validate that platform configurations are available."""
    platforms_configured = []
    
    if DISCORD_WEBHOOK_URL:
        platforms_configured.append("Discord")
    if SLACK_BOT_TOKEN and SLACK_CHANNEL_ID:
        platforms_configured.append("Slack")
    if SENDGRID_API_KEY and EMAIL_FROM and EMAIL_TO:
        platforms_configured.append("Email")
    if TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID:
        platforms_configured.append("Telegram")
    if TWITTER_BEARER_TOKEN:
        platforms_configured.append("Twitter")
    if FACEBOOK_ACCESS_TOKEN and FACEBOOK_PAGE_ID:
        platforms_configured.append("Facebook")
    
    if not platforms_configured:
        logger.warning("No marketing platforms configured. Add API credentials to start posting.")
        logger.info("Available platforms: Discord, Slack, Email, Telegram, Twitter, Facebook")
        return False
    
    logger.info(f"✅ Configured platforms: {', '.join(platforms_configured)}")
    return True

def load_products():
    """Load product data from JSON file."""
    try:
        if not os.path.exists(PRODUCTS_FILE):
            logger.error(f"ERROR: {PRODUCTS_FILE} file not found.")
            logger.error("Please ensure the products.json file exists in the current directory.")
            sys.exit(1)
        
        with open(PRODUCTS_FILE, "r", encoding="utf-8") as f:
            products = json.load(f)
        
        if not products:
            logger.error("ERROR: Products file is empty.")
            sys.exit(1)
        
        if not isinstance(products, list):
            logger.error("ERROR: Products file must contain a JSON array.")
            sys.exit(1)
        
        # Validate product structure
        required_fields = ["title", "description", "url", "image"]
        for i, product in enumerate(products):
            for field in required_fields:
                if field not in product:
                    logger.error(f"ERROR: Product {i+1} is missing required field: {field}")
                    sys.exit(1)
        
        logger.info(f"Successfully loaded {len(products)} products from {PRODUCTS_FILE}")
        return products
    
    except json.JSONDecodeError as e:
        logger.error(f"ERROR: Invalid JSON in {PRODUCTS_FILE}: {e}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"ERROR: Failed to load products: {e}")
        sys.exit(1)

def validate_product(product):
    """Validate product data before posting."""
    required_fields = ["title", "description", "url", "image"]
    for field in required_fields:
        if not product.get(field) or not isinstance(product.get(field), str):
            return False, f"Invalid or missing {field}"
    return True, "Valid"

def post_to_discord(product):
    """Post product to Discord webhook."""
    if not DISCORD_WEBHOOK_URL:
        return False
    
    embed = {
        "title": product["title"],
        "description": product["description"],
        "url": product["url"],
        "image": {"url": product["image"]},
        "color": 3447003,
        "timestamp": datetime.now().isoformat(),
        "footer": {"text": "Product Marketing Bot"}
    }
    
    payload = {"embeds": [embed]}
    
    try:
        response = requests.post(DISCORD_WEBHOOK_URL, json=payload, timeout=REQUEST_TIMEOUT)
        if response.status_code == 204:
            logger.info("✅ Posted to Discord")
            return True
        else:
            logger.error(f"Discord error: {response.status_code}")
            return False
    except Exception as e:
        logger.error(f"Discord posting failed: {e}")
        return False

def post_to_telegram(product):
    """Post product to Telegram."""
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        return False
    
    message = f"🛍️ *{product['title']}*\n\n{product['description']}\n\n[View Product]({product['url']})"
    
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "Markdown",
        "disable_web_page_preview": False
    }
    
    try:
        response = requests.post(url, json=payload, timeout=REQUEST_TIMEOUT)
        if response.status_code == 200:
            logger.info("✅ Posted to Telegram")
            return True
        else:
            logger.error(f"Telegram error: {response.status_code}")
            return False
    except Exception as e:
        logger.error(f"Telegram posting failed: {e}")
        return False

def post_to_slack(product):
    """Post product to Slack."""
    if not SLACK_BOT_TOKEN or not SLACK_CHANNEL_ID:
        return False
    
    from slack_sdk import WebClient
    from slack_sdk.errors import SlackApiError
    
    client = WebClient(token=SLACK_BOT_TOKEN)
    
    blocks = [
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"*{product['title']}*\n{product['description']}"
            },
            "accessory": {
                "type": "image",
                "image_url": product["image"],
                "alt_text": product["title"]
            }
        },
        {
            "type": "actions",
            "elements": [
                {
                    "type": "button",
                    "text": {"type": "plain_text", "text": "View Product"},
                    "url": product["url"]
                }
            ]
        }
    ]
    
    try:
        response = client.chat_postMessage(
            channel=SLACK_CHANNEL_ID,
            blocks=blocks,
            text=f"New product: {product['title']}"
        )
        if response["ok"]:
            logger.info("✅ Posted to Slack")
            return True
        else:
            logger.error(f"Slack error: {response['error']}")
            return False
    except SlackApiError as e:
        logger.error(f"Slack posting failed: {e}")
        return False

def send_email(product):
    """Send product email."""
    if not SENDGRID_API_KEY or not EMAIL_FROM or not EMAIL_TO:
        return False
    
    from sendgrid import SendGridAPIClient
    from sendgrid.helpers.mail import Mail
    
    html_content = f"""
    <h2>{product['title']}</h2>
    <img src="{product['image']}" alt="{product['title']}" style="max-width: 300px;">
    <p>{product['description']}</p>
    <a href="{product['url']}" style="background-color: #007bff; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">View Product</a>
    """
    
    message = Mail(
        from_email=EMAIL_FROM,
        to_emails=EMAIL_TO,
        subject=f"Featured Product: {product['title']}",
        html_content=html_content
    )
    
    try:
        sg = SendGridAPIClient(SENDGRID_API_KEY)
        response = sg.send(message)
        if response.status_code == 202:
            logger.info("✅ Email sent")
            return True
        else:
            logger.error(f"Email error: {response.status_code}")
            return False
    except Exception as e:
        logger.error(f"Email sending failed: {e}")
        return False

def post_product_to_all_platforms(product):
    """Post a product to all configured platforms."""
    # Validate product data
    is_valid, validation_message = validate_product(product)
    if not is_valid:
        logger.error(f"Product validation failed: {validation_message}")
        return False
    
    logger.info(f"🚀 Posting product: {product['title']}")
    
    results = []
    
    # Post to each platform
    results.append(post_to_discord(product))
    results.append(post_to_telegram(product))
    results.append(post_to_slack(product))
    results.append(send_email(product))
    
    successful_posts = sum(results)
    total_configured = sum([
        bool(DISCORD_WEBHOOK_URL),
        bool(TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID),
        bool(SLACK_BOT_TOKEN and SLACK_CHANNEL_ID),
        bool(SENDGRID_API_KEY and EMAIL_FROM and EMAIL_TO)
    ])
    
    logger.info(f"📊 Posted to {successful_posts}/{total_configured} platforms")
    
    return successful_posts > 0

def select_random_product(products):
    """Select a random product from the catalog."""
    if not products:
        logger.error("No products available for selection")
        return None
    
    selected_product = random.choice(products)
    logger.info(f"🎯 Selected product: {selected_product['title']}")
    return selected_product

def main():
    """Main execution function."""
    logger.info("🚀 Starting Multi-Platform Product Marketing Automation")
    logger.info(f"Timestamp: {datetime.now().isoformat()}")
    
    # Validate environment
    has_platforms = validate_environment()
    if not has_platforms:
        logger.info("💡 Configure platform credentials to start automated posting!")
        sys.exit(0)
    
    # Load products
    products = load_products()
    
    # Select random product
    selected_product = select_random_product(products)
    if not selected_product:
        logger.error("Failed to select a product")
        sys.exit(1)
    
    # Post product to all platforms
    success = post_product_to_all_platforms(selected_product)
    
    if success:
        logger.info("✅ Multi-platform automation completed successfully")
        sys.exit(0)
    else:
        logger.error("❌ No platforms posted successfully")
        sys.exit(1)

if __name__ == "__main__":
    main()
