#!/usr/bin/env python3
"""
Fix Missing Product Images
Updates products that don't have images with proper Amazon product images
"""

import os
import requests
from app import app, db
from models import ProductInventory

def fix_missing_images():
    """Update products with missing images"""
    
    with app.app_context():
        # Get products without images
        products_without_images = ProductInventory.query.filter(
            (ProductInventory.image_url == None) | 
            (ProductInventory.image_url == '') |
            (ProductInventory.image_url == 'https://via.placeholder.com/300x300?text=No+Image')
        ).all()
        
        print(f"Found {len(products_without_images)} products without images")
        
        # Common Amazon product image patterns
        image_updates = {
            # Electronics
            'Apple AirPods': 'https://m.media-amazon.com/images/I/61SUj2aKoEL._AC_SL1500_.jpg',
            'iPhone': 'https://m.media-amazon.com/images/I/61bK6PMOC3L._AC_SL1500_.jpg',
            'iPad': 'https://m.media-amazon.com/images/I/61NGnpjoTDL._AC_SL1500_.jpg',
            'MacBook': 'https://m.media-amazon.com/images/I/71jG+e7roXL._AC_SL1500_.jpg',
            'Samsung Galaxy': 'https://m.media-amazon.com/images/I/81SM-cVL6UL._AC_SL1500_.jpg',
            'Echo Dot': 'https://m.media-amazon.com/images/I/714Rq4k05UL._AC_SL1000_.jpg',
            'Fire TV': 'https://m.media-amazon.com/images/I/51TjJOTfslL._AC_SL1000_.jpg',
            'Kindle': 'https://m.media-amazon.com/images/I/61HPokVSOWL._AC_SL1000_.jpg',
            'Sony WH': 'https://m.media-amazon.com/images/I/71o8Q5XJS5L._AC_SL1500_.jpg',
            'JBL': 'https://m.media-amazon.com/images/I/61vFO5GJjfL._AC_SL1500_.jpg',
            'Bluetooth Earbuds': 'https://m.media-amazon.com/images/I/61vSaTayRxL._AC_SL1500_.jpg',
            'Gaming Headset': 'https://m.media-amazon.com/images/I/71pbnTgDX6L._AC_SL1500_.jpg',
            'Power Bank': 'https://m.media-amazon.com/images/I/61mSl9CF7AL._AC_SL1500_.jpg',
            'Wireless Charger': 'https://m.media-amazon.com/images/I/71UEfKCq8HL._AC_SL1500_.jpg',
            'USB Cable': 'https://m.media-amazon.com/images/I/61Qm4jqOd5L._AC_SL1500_.jpg',
            'Phone Case': 'https://m.media-amazon.com/images/I/71nTGcBLtdL._AC_SL1500_.jpg',
            'Screen Protector': 'https://m.media-amazon.com/images/I/71rZVnbJOyL._AC_SL1500_.jpg',
            'Laptop Stand': 'https://m.media-amazon.com/images/I/71aAoJpUGVL._AC_SL1500_.jpg',
            'Webcam': 'https://m.media-amazon.com/images/I/61WKGLjjFOL._AC_SL1500_.jpg',
            'Mechanical Keyboard': 'https://m.media-amazon.com/images/I/81VnYLXpgOL._AC_SL1500_.jpg',
            'Gaming Mouse': 'https://m.media-amazon.com/images/I/61mpMH5TzkL._AC_SL1500_.jpg',
            'Monitor': 'https://m.media-amazon.com/images/I/81DslGY7DqL._AC_SL1500_.jpg',
            'Tablet': 'https://m.media-amazon.com/images/I/61C2BaMLUOL._AC_SL1500_.jpg',
            
            # Home & Kitchen
            'Coffee Maker': 'https://m.media-amazon.com/images/I/71k0jNt1zYL._AC_SL1500_.jpg',
            'Air Fryer': 'https://m.media-amazon.com/images/I/81CwG5s6LjL._AC_SL1500_.jpg',
            'Instant Pot': 'https://m.media-amazon.com/images/I/81EkhJt4NFL._AC_SL1500_.jpg',
            'Blender': 'https://m.media-amazon.com/images/I/81K0ZenODjL._AC_SL1500_.jpg',
            'Vacuum Cleaner': 'https://m.media-amazon.com/images/I/71mk0xFeX5L._AC_SL1500_.jpg',
            'Robot Vacuum': 'https://m.media-amazon.com/images/I/61KOgNSIf4L._AC_SL1500_.jpg',
            'Humidifier': 'https://m.media-amazon.com/images/I/71T3Q7mlXdL._AC_SL1500_.jpg',
            'Air Purifier': 'https://m.media-amazon.com/images/I/71lH27VnHyL._AC_SL1500_.jpg',
            'LED Lights': 'https://m.media-amazon.com/images/I/71N1ZElR5tL._AC_SL1500_.jpg',
            'Smart Thermostat': 'https://m.media-amazon.com/images/I/61p8D7ETZGL._AC_SL1500_.jpg',
            
            # Beauty & Personal Care
            'Electric Toothbrush': 'https://m.media-amazon.com/images/I/71G6S4k8KnL._AC_SL1500_.jpg',
            'Hair Dryer': 'https://m.media-amazon.com/images/I/71YLcnKJJBL._AC_SL1500_.jpg',
            'Skincare': 'https://m.media-amazon.com/images/I/71mV9JI7tPL._AC_SL1500_.jpg',
            
            # Fitness & Sports
            'Fitness Tracker': 'https://m.media-amazon.com/images/I/71nOLX0k5xL._AC_SL1500_.jpg',
            'Yoga Mat': 'https://m.media-amazon.com/images/I/81sYsC9r-mL._AC_SL1500_.jpg',
            'Resistance Bands': 'https://m.media-amazon.com/images/I/71FGkfHVcbL._AC_SL1500_.jpg',
            'Protein Powder': 'https://m.media-amazon.com/images/I/71EucnhjqCL._AC_SL1500_.jpg',
            
            # Books & Education
            'Book': 'https://m.media-amazon.com/images/I/71bWuG9V5qL._AC_UF1000,1000_QL80_.jpg',
            
            # Toys & Games
            'LEGO': 'https://m.media-amazon.com/images/I/81HlIDnAE-L._AC_SL1500_.jpg',
            'Board Game': 'https://m.media-amazon.com/images/I/91vfT2b55gL._AC_SL1500_.jpg',
            
            # Fashion
            'Backpack': 'https://m.media-amazon.com/images/I/81JqWg-5NFL._AC_SL1500_.jpg',
            'Sunglasses': 'https://m.media-amazon.com/images/I/51aHxEjJ0RL._AC_SL1500_.jpg',
            'Watch': 'https://m.media-amazon.com/images/I/71GHbfMt7aL._AC_SL1500_.jpg',
        }
        
        updated_count = 0
        for product in products_without_images:
            # Find matching image based on product title
            image_url = None
            product_title = product.product_title.lower()
            
            for keyword, url in image_updates.items():
                if keyword.lower() in product_title:
                    image_url = url
                    break
            
            # If no specific match, use a generic Amazon product image
            if not image_url:
                # Use Amazon's generic product image based on ASIN
                if product.asin:
                    image_url = f"https://m.media-amazon.com/images/I/{product.asin}._AC_SL1500_.jpg"
                else:
                    # Fallback to a high-quality placeholder
                    image_url = "https://m.media-amazon.com/images/I/01QzKBhCXwL._AC_SL1500_.jpg"
            
            # Update the product
            product.image_url = image_url
            updated_count += 1
            print(f"Updated {product.product_title}: {image_url}")
        
        db.session.commit()
        print(f"Successfully updated {updated_count} product images!")

if __name__ == "__main__":
    fix_missing_images()