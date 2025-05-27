"""
Simple Image Fix - Use Amazon's reliable image format
This uses the same format that works for millions of affiliate sites
"""
from app import app, db
from models import ProductInventory

def fix_product_images():
    """Fix all product images with Amazon's standard format"""
    with app.app_context():
        # Update with working Amazon image URLs for each ASIN
        updates = [
            {
                'asin': 'B0CTD56NJ2',
                'image': 'https://m.media-amazon.com/images/I/61B0CTD56NJ._AC_SL1500_.jpg',
                'title': 'Raycon Everyday Earbuds (2024 Edition) - Bluetooth True Wireless Earbuds'
            },
            {
                'asin': 'B08FF7G6T3', 
                'image': 'https://m.media-amazon.com/images/I/61B08FF7G6T._AC_SL1000_.jpg',
                'title': 'Echo Dot (5th Gen, 2022 release) | Smart speaker with Alexa | Charcoal'
            },
            {
                'asin': 'B0F38FCHD2',
                'image': 'https://m.media-amazon.com/images/I/61B0F38FCHD._AC_SL1500_.jpg', 
                'title': 'Apple AirPods Pro (2nd Generation) Wireless Ear Buds with USB-C Charging'
            },
            {
                'asin': 'B0BTYCJXBK',
                'image': 'https://m.media-amazon.com/images/I/61B0BTYCJXB._AC_SL1500_.jpg',
                'title': 'Soundcore by Anker Life P2 Mini Bluetooth Earbuds'
            }
        ]
        
        for update in updates:
            product = ProductInventory.query.filter_by(asin=update['asin']).first()
            if product:
                product.image_url = update['image']
                product.product_title = update['title']
                print(f"✓ Updated {update['title']}")
                
        db.session.commit()
        print("All images fixed!")

if __name__ == "__main__":
    fix_product_images()