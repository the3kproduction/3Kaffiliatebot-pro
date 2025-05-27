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
        
        # Try multiple selectors to find the main product image
        image_selectors = [
            '#landingImage',
            '#imgBlkFront',
            '.a-dynamic-image',
            '[data-a-image-name="landingImage"]',
            '.a-spacing-small img'
        ]
        
        for selector in image_selectors:
            img_element = soup.select_one(selector)
            if img_element and img_element.get('src'):
                image_url = img_element['src']
                # Clean up the URL to get high quality version
                if 'images-na.ssl-images-amazon.com' in image_url or 'm.media-amazon.com' in image_url:
                    return image_url
                    
        # If no image found, try data-src attribute
        for selector in image_selectors:
            img_element = soup.select_one(selector)
            if img_element and img_element.get('data-src'):
                return img_element['data-src']
                
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