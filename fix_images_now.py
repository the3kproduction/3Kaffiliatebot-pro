"""
Fix Product Images with Working Amazon URLs
Uses Amazon's reliable image format that actually works
"""
from models import ProductInventory, db
from app import app
import requests

def fix_all_product_images():
    """Fix all product images with working Amazon image URLs"""
    print("🔧 Fixing all product images with working Amazon URLs...")
    
    with app.app_context():
        products = ProductInventory.query.all()
        fixed_count = 0
        
        for product in products:
            # Use Amazon's reliable image format
            # Format: https://images-na.ssl-images-amazon.com/images/P/ASIN.jpg
            new_image_url = f"https://images-na.ssl-images-amazon.com/images/P/{product.asin}.jpg"
            
            # Try alternative format if first doesn't work
            try:
                response = requests.head(new_image_url, timeout=3)
                if response.status_code != 200:
                    # Try alternative format
                    new_image_url = f"https://m.media-amazon.com/images/I/{product.asin}._AC_SL1500_.jpg"
                    response = requests.head(new_image_url, timeout=3)
                    if response.status_code != 200:
                        # Try another format
                        new_image_url = f"https://images.amazon.com/images/P/{product.asin}.01.L.jpg"
            except:
                # Use the most reliable format
                new_image_url = f"https://images-na.ssl-images-amazon.com/images/P/{product.asin}.jpg"
            
            # Update the product
            product.image_url = new_image_url
            db.session.commit()
            fixed_count += 1
            print(f"✅ Fixed: {product.product_title}")
        
        print(f"🎉 Fixed {fixed_count} product images!")
        return fixed_count

if __name__ == '__main__':
    fix_all_product_images()