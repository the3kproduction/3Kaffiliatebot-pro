#!/usr/bin/env python3

"""
Fix Products Script - Get Real Amazon Products with Names and Details
"""

import sys
sys.path.append('.')

from app import app, db
from models import ProductInventory
from amazon_scraper import AmazonProductScraper
from inventory_manager import InventoryManager
import time

def fix_products():
    """Replace Unknown Products with real Amazon products"""
    
    with app.app_context():
        # Count current products
        total_products = ProductInventory.query.count()
        unknown_products = ProductInventory.query.filter(ProductInventory.product_title == 'Unknown Product').count()
        
        print(f"🔍 Current inventory: {total_products} total products")
        print(f"❌ Products with missing names: {unknown_products}")
        
        if unknown_products > 0:
            print(f"🧹 Updating {unknown_products} products with real Amazon data...")
            
            scraper = AmazonProductScraper()
            inventory = InventoryManager()
            
            # Get fresh trending products from Amazon
            categories = ["Electronics", "Home & Kitchen", "Sports & Outdoors", "Health & Personal Care"]
            updated_count = 0
            
            for category in categories:
                try:
                    print(f"📦 Getting {category} products...")
                    fresh_products = scraper.get_top_products_by_category(category, limit=15)
                    
                    for product in fresh_products:
                        if product.get('title') and product.get('title') != 'Unknown Product':
                            # Update or add product
                            inventory.add_product_to_inventory(product)
                            updated_count += 1
                            print(f"✅ {updated_count}: {product.get('title', 'Product')[:50]}...")
                            
                    time.sleep(1)  # Be respectful
                    
                except Exception as e:
                    print(f"⚠️ Error with {category}: {e}")
                    
            print(f"\n🎉 Successfully processed {updated_count} products!")
            
        # Show final count
        final_total = ProductInventory.query.count()
        good_products = ProductInventory.query.filter(ProductInventory.product_title != 'Unknown Product').count()
        
        print(f"📊 Final inventory: {final_total} total products")
        print(f"✅ Products with proper names: {good_products}")
        print(f"❌ Still need fixing: {final_total - good_products}")

if __name__ == '__main__':
    fix_products()