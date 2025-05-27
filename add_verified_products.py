#!/usr/bin/env python3
"""
Add More Verified Amazon Products
"""

import sys
import os
from datetime import datetime

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app, db
from models import ProductInventory

def add_more_products():
    """Add more verified Amazon products with working images"""
    products = [
        {
            'asin': 'B07YTF4YQK',
            'title': 'JBL Clip 3 Portable Bluetooth Speaker',
            'price': '$39.95',
            'rating': 4.5,
            'image_url': 'https://m.media-amazon.com/images/I/71fKDYWpnNL._AC_SL1500_.jpg',
            'category': 'Electronics'
        },
        {
            'asin': 'B08J6F2ZTX',
            'title': 'Razer DeathAdder V3 Gaming Mouse',
            'price': '$69.99',
            'rating': 4.4,
            'image_url': 'https://m.media-amazon.com/images/I/61QvbpYKWiL._AC_SL1500_.jpg',
            'category': 'Electronics'
        },
        {
            'asin': 'B0B7BP6CJN',
            'title': 'Govee Immersion TV Light Strip',
            'price': '$89.99',
            'rating': 4.3,
            'image_url': 'https://m.media-amazon.com/images/I/61++WXNHQOL._AC_SL1500_.jpg',
            'category': 'Electronics'
        },
        {
            'asin': 'B09WDD2NWZ',
            'title': 'Ninja Creami Ice Cream Maker',
            'price': '$199.99',
            'rating': 4.4,
            'image_url': 'https://m.media-amazon.com/images/I/71M3+vO4GnL._AC_SL1500_.jpg',
            'category': 'Kitchen'
        },
        {
            'asin': 'B09B8RRQTY',
            'title': 'Apple MagSafe Charger',
            'price': '$39.00',
            'rating': 4.5,
            'image_url': 'https://m.media-amazon.com/images/I/61QKno7GRCL._AC_SL1500_.jpg',
            'category': 'Electronics'
        },
        {
            'asin': 'B09JNQQBMY',
            'title': 'Logitech MX Master 3S Wireless Mouse',
            'price': '$99.99',
            'rating': 4.6,
            'image_url': 'https://m.media-amazon.com/images/I/61YHLZlEGYL._AC_SL1500_.jpg',
            'category': 'Electronics'
        },
        {
            'asin': 'B08GKL3DDS',
            'title': 'Hydro Flask Water Bottle 32 oz',
            'price': '$44.95',
            'rating': 4.7,
            'image_url': 'https://m.media-amazon.com/images/I/61FPo6++rBL._AC_SL1500_.jpg',
            'category': 'Sports'
        },
        {
            'asin': 'B08QHL9LBJ',
            'title': 'Roku Streaming Stick 4K+',
            'price': '$49.99',
            'rating': 4.5,
            'image_url': 'https://m.media-amazon.com/images/I/51+Pl1++9RL._AC_SL1500_.jpg',
            'category': 'Electronics'
        },
        {
            'asin': 'B0C1SLD1PZ',
            'title': 'Carhartt Insulated Work Gloves',
            'price': '$24.99',
            'rating': 4.4,
            'image_url': 'https://m.media-amazon.com/images/I/81QvGWvg8vL._AC_SL1500_.jpg',
            'category': 'Clothing'
        },
        {
            'asin': 'B09DFCB8J8',
            'title': 'Bluetti Portable Power Station',
            'price': '$299.99',
            'rating': 4.3,
            'image_url': 'https://m.media-amazon.com/images/I/71nvZqO5jLL._AC_SL1500_.jpg',
            'category': 'Electronics'
        }
    ]
    
    with app.app_context():
        added = 0
        for product_data in products:
            try:
                existing = ProductInventory.query.filter_by(asin=product_data['asin']).first()
                if existing:
                    print(f"⚠️ Product {product_data['asin']} already exists")
                    continue
                    
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
        
        print(f"\n🎉 Added {added} more verified Amazon products!")

if __name__ == "__main__":
    add_more_products()