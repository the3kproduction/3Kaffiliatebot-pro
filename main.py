#!/usr/bin/env python3
"""
Product Marketing Automation Script

This script randomly selects products from a JSON catalog and posts them
to Zapier webhooks for automated marketing campaigns.
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
WEBHOOK_URL = os.getenv("WEBHOOK_URL")
PRODUCTS_FILE = "products.json"
REQUEST_TIMEOUT = 30  # seconds

def validate_environment():
    """Validate that required environment variables are set."""
    if not WEBHOOK_URL:
        logger.error("ERROR: WEBHOOK_URL environment variable is not set.")
        logger.error("Please create a .env file with your Zapier webhook URL.")
        logger.error("Example: WEBHOOK_URL=https://hooks.zapier.com/hooks/catch/your-id/your-token")
        sys.exit(1)
    
    logger.info(f"Webhook URL configured: {WEBHOOK_URL[:50]}...")

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

def post_product(product):
    """Post a product to the webhook endpoint."""
    # Validate product data
    is_valid, validation_message = validate_product(product)
    if not is_valid:
        logger.error(f"Product validation failed: {validation_message}")
        return False
    
    # Prepare payload
    payload = {
        "title": product["title"],
        "description": product["description"],
        "url": product["url"],
        "image": product["image"],
        "timestamp": datetime.now().isoformat(),
        "source": "automation_script"
    }
    
    # Set request headers
    headers = {
        "Content-Type": "application/json",
        "User-Agent": "Product-Marketing-Bot/1.0"
    }
    
    try:
        logger.info(f"Posting product: {product['title']}")
        logger.debug(f"Payload: {json.dumps(payload, indent=2)}")
        
        response = requests.post(
            WEBHOOK_URL,
            json=payload,
            headers=headers,
            timeout=REQUEST_TIMEOUT
        )
        
        # Check response status
        if response.status_code in (200, 201, 202):
            logger.info(f"✅ Successfully posted: {product['title']}")
            logger.info(f"Response status: {response.status_code}")
            if response.text:
                logger.debug(f"Response body: {response.text[:200]}...")
            return True
        else:
            logger.error(f"❌ Failed to post: {product['title']}")
            logger.error(f"Status code: {response.status_code}")
            logger.error(f"Response: {response.text[:500]}")
            return False
    
    except requests.exceptions.Timeout:
        logger.error(f"❌ Timeout error posting product: {product['title']}")
        logger.error(f"Request timed out after {REQUEST_TIMEOUT} seconds")
        return False
    except requests.exceptions.ConnectionError:
        logger.error(f"❌ Connection error posting product: {product['title']}")
        logger.error("Unable to connect to webhook URL")
        return False
    except requests.exceptions.RequestException as e:
        logger.error(f"❌ Request error posting product: {product['title']}")
        logger.error(f"Error details: {e}")
        return False
    except Exception as e:
        logger.error(f"❌ Unexpected error posting product: {product['title']}")
        logger.error(f"Error details: {e}")
        return False

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
    logger.info("🚀 Starting Product Marketing Automation Script")
    logger.info(f"Timestamp: {datetime.now().isoformat()}")
    
    # Validate environment
    validate_environment()
    
    # Load products
    products = load_products()
    
    # Select random product
    selected_product = select_random_product(products)
    if not selected_product:
        logger.error("Failed to select a product")
        sys.exit(1)
    
    # Post product to webhook
    success = post_product(selected_product)
    
    if success:
        logger.info("✅ Automation completed successfully")
        sys.exit(0)
    else:
        logger.error("❌ Automation failed")
        sys.exit(1)

if __name__ == "__main__":
    main()
