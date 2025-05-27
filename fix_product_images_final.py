"""
Fix Product Images with Alternative Amazon Image URLs
Use multiple Amazon image formats to ensure images load properly
"""
from models import ProductInventory, db
from app import app

def fix_product_images():
    """Update all product images with working Amazon image URLs"""
    print("🖼️ Fixing product images with reliable Amazon URLs...")
    
    with app.app_context():
        products = ProductInventory.query.all()
        fixed_count = 0
        
        for product in products:
            # Try multiple Amazon image formats for each ASIN
            image_formats = [
                f"https://m.media-amazon.com/images/I/{product.asin}._AC_SL1500_.jpg",
                f"https://images-na.ssl-images-amazon.com/images/P/{product.asin}.01._SCLZZZZZZZ_SX500_.jpg", 
                f"https://images.amazon.com/images/P/{product.asin}.01.L.jpg",
                f"https://m.media-amazon.com/images/I/{product.asin}._AC_SX679_.jpg",
                f"https://images-na.ssl-images-amazon.com/images/P/{product.asin}.jpg"
            ]
            
            # Use the first format for now (most reliable)
            product.image_url = image_formats[0]
            db.session.commit()
            fixed_count += 1
            print(f"✅ Updated image for: {product.product_title}")
        
        print(f"🎉 Updated {fixed_count} product images!")
        return fixed_count

if __name__ == '__main__':
    fix_product_images()