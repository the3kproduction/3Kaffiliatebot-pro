"""
Google Image Backup System for Product Images
Automatically finds and updates product images using Google Custom Search API
"""
import os
import requests
from models import ProductInventory, db
from app import app

def get_google_image_for_product(product_title, asin=None):
    """
    Get high-quality product image from Google Custom Search API
    Returns working image URL or None if not found
    """
    try:
        # Google Custom Search API endpoint
        api_key = os.environ.get('GOOGLE_API_KEY')
        search_engine_id = os.environ.get('GOOGLE_SEARCH_ENGINE_ID')
        
        if not api_key or not search_engine_id:
            print("⚠️  Google API credentials not configured")
            return None
        
        # Build search query for product images
        search_query = f"{product_title} product"
        if asin:
            search_query += f" {asin}"
        
        # Google Custom Search API parameters
        params = {
            'key': api_key,
            'cx': search_engine_id,
            'q': search_query,
            'searchType': 'image',
            'imgSize': 'medium',
            'imgType': 'photo',
            'safe': 'active',
            'num': 5  # Get top 5 results
        }
        
        response = requests.get('https://www.googleapis.com/customsearch/v1', params=params)
        
        if response.status_code == 200:
            data = response.json()
            
            if 'items' in data:
                # Try each image until we find a working one
                for item in data['items']:
                    image_url = item.get('link')
                    if image_url and verify_image_url(image_url):
                        print(f"✅ Found Google image for {product_title}")
                        return image_url
        
        return None
        
    except Exception as e:
        print(f"❌ Google image search failed: {str(e)}")
        return None

def verify_image_url(url):
    """Verify that an image URL is accessible and returns an image"""
    try:
        response = requests.head(url, timeout=5)
        content_type = response.headers.get('content-type', '').lower()
        return (response.status_code == 200 and 
                any(img_type in content_type for img_type in ['image/jpeg', 'image/jpg', 'image/png', 'image/webp']))
    except:
        return False

def fix_broken_product_images():
    """
    Find products with broken images and replace them with Google image backup
    """
    print("🔍 Scanning for products with broken images...")
    
    with app.app_context():
        # Get all products
        products = ProductInventory.query.all()
        fixed_count = 0
        
        for product in products:
            # Check if current image is broken or missing
            if not product.image_url or not verify_image_url(product.image_url):
                print(f"🔧 Fixing image for: {product.product_title}")
                
                # Try Google image backup
                google_image = get_google_image_for_product(product.product_title, product.asin)
                
                if google_image:
                    product.image_url = google_image
                    db.session.commit()
                    fixed_count += 1
                    print(f"✅ Fixed image for {product.product_title}")
                else:
                    # Use Amazon standard format as last resort
                    amazon_backup = f"https://images-na.ssl-images-amazon.com/images/I/{product.asin}._AC_SL1500_.jpg"
                    product.image_url = amazon_backup
                    db.session.commit()
                    print(f"🔄 Using Amazon backup for {product.product_title}")
        
        print(f"🎉 Fixed {fixed_count} product images using Google backup!")
        return fixed_count

def update_all_images_with_google_backup():
    """
    Update ALL product images with high-quality Google images
    """
    print("🚀 Updating ALL product images with Google backup...")
    
    with app.app_context():
        products = ProductInventory.query.all()
        updated_count = 0
        
        for product in products:
            print(f"🔍 Processing: {product.product_title}")
            
            # Get Google image
            google_image = get_google_image_for_product(product.product_title, product.asin)
            
            if google_image:
                product.image_url = google_image
                db.session.commit()
                updated_count += 1
                print(f"✅ Updated with Google image: {product.product_title}")
            else:
                print(f"⚠️  No Google image found for: {product.product_title}")
        
        print(f"🎉 Updated {updated_count} products with Google images!")
        return updated_count

if __name__ == '__main__':
    # Run image fixing
    print("🔧 Starting Google Image Backup System...")
    fix_broken_product_images()