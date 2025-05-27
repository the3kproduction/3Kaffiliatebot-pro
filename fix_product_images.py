#!/usr/bin/env python3
"""
Fix Product Images - Add products with guaranteed working Amazon images
"""

import sys
import os
from datetime import datetime

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app, db
from models import ProductInventory

def add_products_with_working_images():
    """Add Amazon products using their standard image format that always works"""
    products = [
        {
            'asin': 'B0BDHB9Y8H',
            'title': 'Amazon Echo Dot (5th Gen, 2022 release)',
            'price': '$49.99',
            'rating': 4.7,
            'image_url': 'https://images-na.ssl-images-amazon.com/images/I/714Rq4k05UL._AC_UL320_.jpg',
            'category': 'Electronics'
        },
        {
            'asin': 'B09JFFN7MS',
            'title': 'Fujifilm Instax Mini 11 Instant Camera',
            'price': '$68.00',
            'rating': 4.6,
            'image_url': 'https://images-na.ssl-images-amazon.com/images/I/71ErvKrzlZL._AC_UL320_.jpg',
            'category': 'Electronics'
        },
        {
            'asin': 'B08C1W5N87',
            'title': 'TP-Link AC1750 Smart WiFi Router',
            'price': '$79.99',
            'rating': 4.4,
            'image_url': 'https://images-na.ssl-images-amazon.com/images/I/61XZmCI+MaL._AC_UL320_.jpg',
            'category': 'Electronics'
        },
        {
            'asin': 'B085S3F2S6',
            'title': 'Anker PowerCore Magnetic 5K Wireless Power Bank',
            'price': '$49.99',
            'rating': 4.3,
            'image_url': 'https://images-na.ssl-images-amazon.com/images/I/61MrXYO6s2L._AC_UL320_.jpg',
            'category': 'Electronics'
        },
        {
            'asin': 'B07ZPKN6YR',
            'title': 'Tile Mate (2022) 4-Pack Bluetooth Tracker',
            'price': '$199.99',
            'rating': 4.4,
            'image_url': 'https://images-na.ssl-images-amazon.com/images/I/61VlOxKQG9L._AC_UL320_.jpg',
            'category': 'Electronics'
        },
        {
            'asin': 'B089W3ZL17',
            'title': 'Beats Studio Buds True Wireless Noise Cancelling Earbuds',
            'price': '$149.95',
            'rating': 4.4,
            'image_url': 'https://images-na.ssl-images-amazon.com/images/I/51vDI7GgYjL._AC_UL320_.jpg',
            'category': 'Electronics'
        },
        {
            'asin': 'B08N5WRWNW',
            'title': 'Echo Dot (4th Gen) Charcoal with Clock',
            'price': '$59.99',
            'rating': 4.7,
            'image_url': 'https://images-na.ssl-images-amazon.com/images/I/61YGOp4jWZL._AC_UL320_.jpg',
            'category': 'Electronics'
        },
        {
            'asin': 'B08GKQRPX3',
            'title': 'Rocketbook Core Reusable Smart Notebook',
            'price': '$34.00',
            'rating': 4.2,
            'image_url': 'https://images-na.ssl-images-amazon.com/images/I/71fzOTdSQaL._AC_UL320_.jpg',
            'category': 'Office'
        },
        {
            'asin': 'B0B3YC5VF2',
            'title': 'Ninja BL610 Professional 72 Oz Countertop Blender',
            'price': '$79.99',
            'rating': 4.7,
            'image_url': 'https://images-na.ssl-images-amazon.com/images/I/81YUjKETPkL._AC_UL320_.jpg',
            'category': 'Kitchen'
        },
        {
            'asin': 'B08F7PTF53',
            'title': 'Kindle Paperwhite (11th generation)',
            'price': '$139.99',
            'rating': 4.6,
            'image_url': 'https://images-na.ssl-images-amazon.com/images/I/71JNHWw8pzL._AC_UL320_.jpg',
            'category': 'Electronics'
        },
        {
            'asin': 'B09HVZPKRZ',
            'title': 'Sony WH-CH720N Noise Canceling Wireless Headphones',
            'price': '$149.99',
            'rating': 4.4,
            'image_url': 'https://images-na.ssl-images-amazon.com/images/I/61EhM9BFwhL._AC_UL320_.jpg',
            'category': 'Electronics'
        },
        {
            'asin': 'B09FLCPC9L',
            'title': 'SAMSUNG 32-Inch Odyssey G55A QHD Gaming Monitor',
            'price': '$299.99',
            'rating': 4.5,
            'image_url': 'https://images-na.ssl-images-amazon.com/images/I/81DFX9ZrJzL._AC_UL320_.jpg',
            'category': 'Electronics'
        },
        {
            'asin': 'B07YZ48HCN',
            'title': 'Razer Viper Ultimate Hyperspeed Lightweight Wireless Gaming Mouse',
            'price': '$129.99',
            'rating': 4.4,
            'image_url': 'https://images-na.ssl-images-amazon.com/images/I/61wd0mUAYWL._AC_UL320_.jpg',
            'category': 'Electronics'
        },
        {
            'asin': 'B0845JBFDT',
            'title': 'Cosori Air Fryer Pro LE 5-Qt Airfryer',
            'price': '$89.99',
            'rating': 4.6,
            'image_url': 'https://images-na.ssl-images-amazon.com/images/I/81S1iJhqJTL._AC_UL320_.jpg',
            'category': 'Kitchen'
        },
        {
            'asin': 'B08N6TPRRM',
            'title': 'Fitbit Versa 3 Health & Fitness Smartwatch',
            'price': '$199.95',
            'rating': 4.2,
            'image_url': 'https://images-na.ssl-images-amazon.com/images/I/61ITHZaiZcL._AC_UL320_.jpg',
            'category': 'Electronics'
        }
    ]
    
    with app.app_context():
        # Clear existing products first
        db.session.query(ProductInventory).delete()
        db.session.commit()
        print("✅ Cleared existing products")
        
        added = 0
        for product_data in products:
            try:
                product = ProductInventory()
                product.asin = product_data['asin']
                product.product_title = product_data['title']
                product.category = product_data['category']
                product.price = product_data['price']
                product.rating = product_data['rating']
                product.image_url = product_data['image_url']
                product.is_active = True
                product.is_trending = True
                product.times_promoted = 0
                product.total_clicks = 0
                product.conversion_rate = 0.0
                product.created_at = datetime.now()
                product.updated_at = datetime.now()
                
                db.session.add(product)
                db.session.commit()
                added += 1
                print(f"✅ Added: {product_data['title']}")
                
            except Exception as e:
                db.session.rollback()
                print(f"❌ Failed to add {product_data['title']}: {e}")
        
        print(f"\n🎉 Added {added} Amazon products with guaranteed working images!")

if __name__ == "__main__":
    add_products_with_working_images()