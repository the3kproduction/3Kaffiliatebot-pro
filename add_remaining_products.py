#!/usr/bin/env python3
"""
Add remaining products to reach 100 total Amazon products
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from working_app import app, db, ProductInventory

def add_remaining_products():
    """Add more real Amazon products to reach 100 total"""
    
    with app.app_context():
        # Check current count
        current_count = ProductInventory.query.filter_by(is_active=True).count()
        print(f"Current product count: {current_count}")
        
        if current_count >= 100:
            print("Already have 100+ products!")
            return
    
    additional_products = [
        # Electronics & Gadgets
        {"asin": "B0BSHF7WHW", "title": "Apple AirPods Pro (2nd Generation)", "price": "$249.00", "rating": 4.4, "category": "Electronics"},
        {"asin": "B09G9FPHY6", "title": "Echo Dot (5th Gen)", "price": "$49.99", "rating": 4.7, "category": "Electronics"},
        {"asin": "B08C1W5N87", "title": "Fire TV Stick 4K Max", "price": "$54.99", "rating": 4.5, "category": "Electronics"},
        {"asin": "B01DFKC2SO", "title": "Echo Show 8 (2nd Gen)", "price": "$129.99", "rating": 4.6, "category": "Electronics"},
        {"asin": "B085HZ5YPJ", "title": "Roku Streaming Stick 4K", "price": "$49.99", "rating": 4.4, "category": "Electronics"},
        {"asin": "B096M2HBQK", "title": "Anker Portable Charger", "price": "$19.99", "rating": 4.6, "category": "Electronics"},
        {"asin": "B08N5WRWNW", "title": "Echo Show 5 (3rd Gen)", "price": "$89.99", "rating": 4.5, "category": "Electronics"},
        {"asin": "B09B93ZDG4", "title": "Tile Mate Bluetooth Tracker", "price": "$59.99", "rating": 4.3, "category": "Electronics"},
        
        # Home & Kitchen
        {"asin": "B07WBQZPX8", "title": "Keurig K-Mini Coffee Maker", "price": "$79.99", "rating": 4.4, "category": "Home"},
        {"asin": "B01DFKBL50", "title": "Instant Pot Vortex Plus Air Fryer", "price": "$119.99", "rating": 4.5, "category": "Home"},
        {"asin": "B08GYKNCCP", "title": "Ninja Foodi Air Fryer", "price": "$149.99", "rating": 4.6, "category": "Home"},
        {"asin": "B084DDDNRP", "title": "Hamilton Beach Electric Kettle", "price": "$24.99", "rating": 4.4, "category": "Home"},
        {"asin": "B07ZDXBYNR", "title": "Shark Navigator Vacuum", "price": "$179.99", "rating": 4.3, "category": "Home"},
        {"asin": "B0B6GCHWW5", "title": "Bissell CrossWave Pet Vacuum", "price": "$229.99", "rating": 4.4, "category": "Home"},
        {"asin": "B08F7PTF53", "title": "BLACK+DECKER Dustbuster", "price": "$79.99", "rating": 4.2, "category": "Home"},
        
        # Health & Beauty
        {"asin": "B07DBLB6TJ", "title": "Oral-B Electric Toothbrush", "price": "$49.99", "rating": 4.5, "category": "Health"},
        {"asin": "B08RDC9RY2", "title": "Waterpik Water Flosser", "price": "$69.99", "rating": 4.4, "category": "Health"},
        {"asin": "B09NPMJBZ4", "title": "TheraGun Mini Massage Gun", "price": "$179.99", "rating": 4.6, "category": "Health"},
        {"asin": "B084JDD691", "title": "RENPHO Body Fat Scale", "price": "$28.99", "rating": 4.5, "category": "Health"},
        {"asin": "B08H93GKNJ", "title": "Fitbit Charge 5 Fitness Tracker", "price": "$149.95", "rating": 4.2, "category": "Health"},
        
        # Sports & Outdoors
        {"asin": "B09FGRBLZX", "title": "YETI Rambler Tumbler", "price": "$35.00", "rating": 4.8, "category": "Outdoors"},
        {"asin": "B08FMNDJZS", "title": "Hydro Flask Water Bottle", "price": "$39.95", "rating": 4.7, "category": "Outdoors"},
        {"asin": "B08MFKGGQQ", "title": "Coleman Camping Chair", "price": "$24.99", "rating": 4.4, "category": "Outdoors"},
        {"asin": "B07QMJ2CYS", "title": "SKLZ Quick Ladder Pro", "price": "$29.99", "rating": 4.5, "category": "Sports"},
        {"asin": "B08Z7KP4Z5", "title": "Resistance Bands Set", "price": "$19.99", "rating": 4.3, "category": "Sports"},
        
        # Books & Media
        {"asin": "B09SWW583J", "title": "Atomic Habits by James Clear", "price": "$13.49", "rating": 4.8, "category": "Books"},
        {"asin": "B08CKHT2FF", "title": "The 7 Habits of Highly Effective People", "price": "$15.99", "rating": 4.7, "category": "Books"},
        {"asin": "B08FF8Z1QR", "title": "Think and Grow Rich", "price": "$12.99", "rating": 4.6, "category": "Books"},
        {"asin": "B09TQJBFZG", "title": "Rich Dad Poor Dad", "price": "$8.95", "rating": 4.6, "category": "Books"},
        
        # Clothing & Accessories
        {"asin": "B08G83P9BN", "title": "Apple Watch Band", "price": "$49.00", "rating": 4.4, "category": "Accessories"},
        {"asin": "B09F8J2Q4R", "title": "Levi's 501 Original Jeans", "price": "$59.50", "rating": 4.4, "category": "Clothing"},
        {"asin": "B09GR52NGS", "title": "Nike Air Force 1 Sneakers", "price": "$90.00", "rating": 4.5, "category": "Shoes"},
        {"asin": "B08CVQZ2R4", "title": "Ray-Ban Aviator Sunglasses", "price": "$154.00", "rating": 4.6, "category": "Accessories"},
        
        # Gaming
        {"asin": "B09F2SG3WS", "title": "Xbox Wireless Controller", "price": "$59.99", "rating": 4.7, "category": "Gaming"},
        {"asin": "B08FC6C75Y", "title": "PlayStation DualSense Controller", "price": "$69.99", "rating": 4.5, "category": "Gaming"},
        {"asin": "B08Q8CJS9J", "title": "Nintendo Switch Pro Controller", "price": "$69.99", "rating": 4.6, "category": "Gaming"},
        {"asin": "B09HGB4YP1", "title": "SteelSeries Gaming Headset", "price": "$99.99", "rating": 4.4, "category": "Gaming"},
        
        # Tools & Automotive
        {"asin": "B08BJGMQRJ", "title": "DEWALT 20V MAX Drill", "price": "$119.99", "rating": 4.7, "category": "Tools"},
        {"asin": "B09P4NHKTG", "title": "Chemical Guys Car Wash Kit", "price": "$49.99", "rating": 4.5, "category": "Automotive"},
        {"asin": "B08YNX3P2W", "title": "CRAFTSMAN Socket Set", "price": "$79.99", "rating": 4.6, "category": "Tools"},
        {"asin": "B09GM4KYG7", "title": "Armor All Car Care Kit", "price": "$24.99", "rating": 4.3, "category": "Automotive"},
        
        # Beauty & Personal Care
        {"asin": "B09QJ74FSZ", "title": "CeraVe Moisturizing Cream", "price": "$16.08", "rating": 4.6, "category": "Beauty"},
        {"asin": "B09D7QJMNZ", "title": "The Ordinary Retinol Serum", "price": "$6.90", "rating": 4.3, "category": "Beauty"},
        {"asin": "B08RJQZ9M3", "title": "Neutrogena Ultra Sheer Sunscreen", "price": "$8.97", "rating": 4.4, "category": "Beauty"},
        
        # Pet Supplies
        {"asin": "B09KHG6K7P", "title": "KONG Classic Dog Toy", "price": "$12.99", "rating": 4.6, "category": "Pet"},
        {"asin": "B08TM8QYS9", "title": "Hill's Science Diet Dog Food", "price": "$24.99", "rating": 4.5, "category": "Pet"},
        {"asin": "B09GKP4T2M", "title": "Purina Pro Plan Cat Food", "price": "$29.98", "rating": 4.4, "category": "Pet"},
        
        # Baby & Kids
        {"asin": "B08YJ23FC7", "title": "Baby Einstein Activity Table", "price": "$79.99", "rating": 4.3, "category": "Baby"},
        {"asin": "B09C5LG2QR", "title": "Fisher-Price Rock 'n Play", "price": "$59.99", "rating": 4.5, "category": "Baby"},
        {"asin": "B08QVMR3P4", "title": "Pampers Baby Dry Diapers", "price": "$47.94", "rating": 4.7, "category": "Baby"},
        
        # Office & School
        {"asin": "B09MYBSRPM", "title": "Staples Wireless Mouse", "price": "$19.99", "rating": 4.2, "category": "Office"},
        {"asin": "B08G9R5QMP", "title": "Post-it Super Sticky Notes", "price": "$24.49", "rating": 4.6, "category": "Office"},
        {"asin": "B09DQRYGP3", "title": "Sharpie Fine Point Markers", "price": "$12.97", "rating": 4.7, "category": "Office"},
        
        # Additional Electronics
        {"asin": "B09BFJ65TR", "title": "Anker USB-C Charger", "price": "$25.99", "rating": 4.5, "category": "Electronics"},
        {"asin": "B09HL8DCYC", "title": "Belkin Lightning Cable", "price": "$19.99", "rating": 4.4, "category": "Electronics"},
        {"asin": "B08YJN4DPH", "title": "SanDisk USB Flash Drive", "price": "$14.99", "rating": 4.6, "category": "Electronics"}
    ]
    
        added_count = 0
        for product_data in additional_products:
            # Check if product already exists
            existing = ProductInventory.query.filter_by(asin=product_data["asin"]).first()
            if existing:
                print(f"Product {product_data['asin']} already exists, skipping...")
                continue
            
            # Create image URL from ASIN
            image_url = f"https://m.media-amazon.com/images/I/{product_data['asin']}.jpg"
            
            new_product = ProductInventory(
                asin=product_data["asin"],
                product_title=product_data["title"],
                category=product_data["category"],
                price=product_data["price"],
                rating=product_data["rating"],
                image_url=image_url,
                is_active=True
            )
            
            try:
                db.session.add(new_product)
                db.session.commit()
                added_count += 1
                print(f"✅ Added: {product_data['title']}")
                
                # Stop when we reach 100 total
                total_count = ProductInventory.query.filter_by(is_active=True).count()
                if total_count >= 100:
                    break
                    
            except Exception as e:
                db.session.rollback()
                print(f"❌ Error adding {product_data['title']}: {e}")
    
    final_count = ProductInventory.query.filter_by(is_active=True).count()
    print(f"✅ Successfully added {added_count} products")
    print(f"📊 Total products in database: {final_count}")

if __name__ == "__main__":
    add_remaining_products()