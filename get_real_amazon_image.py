"""
Get real Amazon product image from product URL
"""
import requests
from bs4 import BeautifulSoup
import re

def get_amazon_product_image(product_url):
    """Extract the main product image from Amazon product page"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.get(product_url, headers=headers)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # First try Open Graph and Twitter Card meta tags (what Discord/social media uses)
        og_image = soup.find('meta', property='og:image')
        if og_image and og_image.get('content'):
            return og_image['content']
            
        twitter_image = soup.find('meta', name='twitter:image')
        if twitter_image and twitter_image.get('content'):
            return twitter_image['content']
            
        # Try other meta image tags
        meta_image = soup.find('meta', {'name': 'image'})
        if meta_image and meta_image.get('content'):
            return meta_image['content']
            
        # As fallback, try the main product image selectors
        image_selectors = [
            '#landingImage',
            '#imgBlkFront', 
            '.a-dynamic-image'
        ]
        
        for selector in image_selectors:
            img_element = soup.select_one(selector)
            if img_element:
                src = img_element.get('src') or img_element.get('data-src')
                if src and ('amazon' in src):
                    return src
                
        print(f"Could not find image for {product_url}")
        return None
        
    except Exception as e:
        print(f"Error getting image for {product_url}: {e}")
        return None

if __name__ == "__main__":
    # Test with the provided URL
    url = "https://www.amazon.com/Soundcore-Wireless-Bluetooth-Water-Resistant-Customization/dp/B0BTYCJXBK/"
    image_url = get_amazon_product_image(url)
    if image_url:
        print(f"Found image URL: {image_url}")
    else:
        print("No image found")