#!/usr/bin/env python3
"""
Product Population Script
Automatically scrapes Amazon for trending products and populates the inventory
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app, db
from inventory_manager import InventoryManager
from amazon_scraper import AmazonProductScraper
from enhanced_image_scraper import ProductImageScraper
import time

def populate_initial_products():
    """Populate database with trending Amazon products"""
    print("🔥 Starting Amazon product population...")
    
    with app.app_context():
        try:
            # Initialize managers
            inventory = InventoryManager()
            scraper = AmazonProductScraper()
            image_scraper = ProductImageScraper()
            
            # Categories to scrape
            categories = [
                "Electronics",
                "Home & Garden", 
                "Sports & Outdoors",
                "Tools & Home Improvement",
                "Toys & Games",
                "Health & Personal Care",
                "Beauty & Personal Care",
                "Kitchen & Dining"
            ]
            
            total_added = 0
            
            for category in categories:
                print(f"\n📦 Scraping {category} products...")
                try:
                    # Get top products from this category
                    products = scraper.get_top_products_by_category(category, limit=15)
                    
                    if products:
                        for product in products:
                            try:
                                # Enhance with better images
                                if product.get('asin'):
                                    better_image = image_scraper.get_amazon_product_image(product['asin'])
                                    if better_image:
                                        product['image_url'] = better_image
                                
                                # Add to inventory
                                success = inventory.add_product_to_inventory(product)
                                if success:
                                    total_added += 1
                                    print(f"✅ Added: {product.get('title', 'Unknown')[:50]}...")
                                else:
                                    print(f"⚠️ Skipped duplicate: {product.get('title', 'Unknown')[:50]}...")
                                    
                            except Exception as e:
                                print(f"❌ Error adding product: {e}")
                                continue
                                
                        # Small delay between products
                        time.sleep(1)
                    else:
                        print(f"⚠️ No products found for {category}")
                        
                except Exception as e:
                    print(f"❌ Error scraping {category}: {e}")
                    continue
                
                # Delay between categories
                time.sleep(2)
            
            print(f"\n🎉 Successfully added {total_added} products to inventory!")
            
            # Also get some general trending products
            print("\n🔥 Getting general trending products...")
            try:
                trending = scraper.get_trending_products(limit=20)
                for product in trending:
                    try:
                        if product.get('asin'):
                            better_image = image_scraper.get_amazon_product_image(product['asin'])
                            if better_image:
                                product['image_url'] = better_image
                        
                        success = inventory.add_product_to_inventory(product)
                        if success:
                            total_added += 1
                            print(f"✅ Added trending: {product.get('title', 'Unknown')[:50]}...")
                    except Exception as e:
                        print(f"❌ Error adding trending product: {e}")
                        continue
                        
            except Exception as e:
                print(f"❌ Error getting trending products: {e}")
            
            print(f"\n🚀 COMPLETE! Total products in inventory: {total_added}")
            print("💰 Your affiliate marketing system is now ready to start earning!")
            
        except Exception as e:
            print(f"❌ Fatal error: {e}")
            return False
            
    return True

if __name__ == "__main__":
    populate_initial_products()