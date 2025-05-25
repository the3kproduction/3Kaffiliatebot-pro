#!/usr/bin/env python3
from app import app, db
from inventory_manager import InventoryManager
from amazon_scraper import AmazonProductScraper
import time

with app.app_context():
    inventory = InventoryManager()
    scraper = AmazonProductScraper()
    
    print('🎯 Getting 40+ more trending Amazon products...')
    
    # Focus on high-converting categories
    high_value_categories = [
        "Beauty & Personal Care",
        "Health & Personal Care", 
        "Sports & Outdoors",
        "Tools & Home Improvement",
        "Toys & Games",
        "Home & Garden",
        "Kitchen & Dining"
    ]
    
    total_added = 0
    target = 40
    
    for category in high_value_categories:
        if total_added >= target:
            break
            
        try:
            print(f'📦 Scraping {category}...')
            products = scraper.get_top_products_by_category(category, limit=8)
            
            for product in products:
                if total_added >= target:
                    break
                    
                success = inventory.add_product_to_inventory(product)
                if success:
                    total_added += 1
                    print(f'✅ {total_added}/40: {product.get("title", "Unknown")[:50]}...')
                    
            time.sleep(1.5)  # Respectful delay
            
        except Exception as e:
            print(f'⚠️ Error with {category}: {e}')
            time.sleep(2)
    
    print(f'\n🚀 Successfully added {total_added} more trending products!')
    
    # Final count
    from models import ProductInventory
    final_total = ProductInventory.query.count()
    print(f'🎉 Total products in inventory: {final_total}')
    print('💰 Your affiliate marketing empire is ready to start making money!')