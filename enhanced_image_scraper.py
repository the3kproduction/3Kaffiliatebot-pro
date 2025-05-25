"""
Enhanced Image Scraper for Amazon Products
Gets high-quality product images without Amazon API
"""
import requests
import re
from bs4 import BeautifulSoup
import logging

logger = logging.getLogger(__name__)

class ProductImageScraper:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
    
    def get_amazon_product_image(self, asin):
        """Get high-quality product image from Amazon product page"""
        try:
            # Go directly to Amazon product page
            url = f"https://www.amazon.com/dp/{asin}"
            response = requests.get(url, headers=self.headers, timeout=10)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Method 1: Look for main product image
                main_image = soup.find('img', {'id': 'landingImage'})
                if main_image and main_image.get('src'):
                    image_url = main_image['src']
                    return self.enhance_image_quality(image_url)
                
                # Method 2: Look for data-old-hires attribute (high-res image)
                main_image = soup.find('img', {'data-old-hires': True})
                if main_image:
                    image_url = main_image['data-old-hires']
                    return self.enhance_image_quality(image_url)
                
                # Method 3: Look for any large product image
                img_tags = soup.find_all('img')
                for img in img_tags:
                    src = img.get('src') or img.get('data-src')
                    if src and 'images-amazon.com' in src and any(size in src for size in ['SX', 'SY', 'AC']):
                        return self.enhance_image_quality(src)
                
                logger.warning(f"No suitable image found for ASIN: {asin}")
                return None
                
        except Exception as e:
            logger.error(f"Error getting image for ASIN {asin}: {e}")
            return None
    
    def enhance_image_quality(self, image_url):
        """Convert Amazon image URL to highest quality version"""
        if not image_url or 'images-amazon.com' not in image_url:
            return image_url
        
        try:
            # Remove existing size parameters and set to high quality
            # Amazon image URL format: https://m.media-amazon.com/images/I/image-id._SIZE_.jpg
            
            # Extract the base image ID
            image_id_match = re.search(r'/images/I/([^._]+)', image_url)
            if image_id_match:
                image_id = image_id_match.group(1)
                # Create high-quality URL (500x500 pixels)
                high_quality_url = f"https://m.media-amazon.com/images/I/{image_id}._AC_SX500_SY500_.jpg"
                return high_quality_url
            
            # Fallback: try to improve existing URL
            enhanced_url = re.sub(r'(\._[A-Z0-9,_]*_\.)', '._AC_SX500_SY500_.', image_url)
            return enhanced_url
            
        except Exception as e:
            logger.error(f"Error enhancing image quality: {e}")
            return image_url
    
    def get_product_images_multiple_sources(self, asin, product_title):
        """Try multiple methods to get product image"""
        
        # Method 1: Direct Amazon scraping
        amazon_image = self.get_amazon_product_image(asin)
        if amazon_image:
            return amazon_image
        
        # Method 2: Use Amazon's standard image URL pattern
        try:
            # Many Amazon products follow this pattern
            standard_url = f"https://m.media-amazon.com/images/I/{asin}._AC_SX500_SY500_.jpg"
            
            # Test if the URL works
            test_response = requests.head(standard_url, headers=self.headers, timeout=5)
            if test_response.status_code == 200:
                return standard_url
        except:
            pass
        
        # Method 3: Alternative Amazon image pattern
        try:
            alt_url = f"https://images-na.ssl-images-amazon.com/images/I/{asin}._AC_SX500_SY500_.jpg"
            test_response = requests.head(alt_url, headers=self.headers, timeout=5)
            if test_response.status_code == 200:
                return alt_url
        except:
            pass
        
        logger.warning(f"Could not find image for ASIN: {asin}")
        return None

def update_product_images():
    """Update existing products with better images"""
    from models import ProductInventory, db
    
    scraper = ProductImageScraper()
    products = ProductInventory.query.filter(
        (ProductInventory.image_url.is_(None)) | 
        (ProductInventory.image_url == '') |
        (ProductInventory.image_url.contains('data:image/svg'))
    ).limit(50).all()
    
    updated_count = 0
    for product in products:
        try:
            new_image = scraper.get_product_images_multiple_sources(product.asin, product.product_title)
            if new_image:
                product.image_url = new_image
                updated_count += 1
                logger.info(f"Updated image for {product.asin}")
        except Exception as e:
            logger.error(f"Error updating image for {product.asin}: {e}")
    
    if updated_count > 0:
        db.session.commit()
        logger.info(f"Updated {updated_count} product images")
    
    return updated_count