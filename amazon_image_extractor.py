"""
Amazon Image Extractor - Gets the same images Discord shows
Uses Amazon's Open Graph and social media preview images
"""
import requests
from bs4 import BeautifulSoup
import re

def get_amazon_preview_image(amazon_url):
    """
    Extract the preview image that Discord/social media sees from Amazon URL
    This is the same image that shows up when you share Amazon links
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate',
        'Connection': 'keep-alive',
    }
    
    try:
        response = requests.get(amazon_url, headers=headers, timeout=10)
        if response.status_code != 200:
            print(f"Failed to fetch {amazon_url}: {response.status_code}")
            return None
            
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Method 1: Look for Open Graph image (what Discord uses)
        og_image = soup.find('meta', {'property': 'og:image'})
        if og_image and og_image.get('content'):
            image_url = og_image['content']
            print(f"Found OG image: {image_url}")
            return image_url
            
        # Method 2: Look for Twitter card image
        twitter_image = soup.find('meta', {'name': 'twitter:image'})
        if twitter_image and twitter_image.get('content'):
            image_url = twitter_image['content']
            print(f"Found Twitter image: {image_url}")
            return image_url
            
        # Method 3: Find the main product image
        # Look for the main product image container
        main_image = soup.find('img', {'id': 'landingImage'})
        if main_image and main_image.get('src'):
            image_url = main_image['src']
            print(f"Found main image: {image_url}")
            return image_url
            
        # Method 4: Look for any high-res Amazon image
        img_tags = soup.find_all('img')
        for img in img_tags:
            src = img.get('src', '')
            if 'images-na.ssl-images-amazon.com' in src or 'm.media-amazon.com' in src:
                if '_AC_' in src:  # High quality Amazon image
                    print(f"Found Amazon image: {src}")
                    return src
                    
        print(f"No image found for {amazon_url}")
        return None
        
    except Exception as e:
        print(f"Error extracting image from {amazon_url}: {e}")
        return None

def fix_all_product_images():
    """Fix all product images using the same method Discord uses"""
    from app import app, db
    from models import ProductInventory
    
    with app.app_context():
        products = ProductInventory.query.all()
        
        for product in products:
            if product.asin:
                # Build Amazon URL from ASIN
                amazon_url = f"https://www.amazon.com/dp/{product.asin}"
                print(f"Getting image for {product.product_title}...")
                
                image_url = get_amazon_preview_image(amazon_url)
                if image_url:
                    product.image_url = image_url
                    print(f"✓ Updated image for {product.product_title}")
                else:
                    print(f"✗ No image found for {product.product_title}")
                    
        db.session.commit()
        print("All product images updated!")

if __name__ == "__main__":
    # Test with your Soundcore product
    test_url = "https://www.amazon.com/Soundcore-Wireless-Bluetooth-Water-Resistant-Customization/dp/B0BTYCJXBK/"
    image = get_amazon_preview_image(test_url)
    if image:
        print(f"SUCCESS: Found image - {image}")
    else:
        print("FAILED: No image found")