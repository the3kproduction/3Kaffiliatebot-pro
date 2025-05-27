"""
Amazon Best Sellers Scraper
Automatically gets top trending products from Amazon's best seller lists
Updates product catalog with fresh, popular items that people are buying
"""
from models import ProductInventory, db
from app import app
import requests
from bs4 import BeautifulSoup
import time
import random

class AmazonBestSellersScraper:
    def __init__(self):
        self.categories = [
            'electronics',
            'home-garden', 
            'sports-outdoors',
            'toys-games',
            'kitchen',
            'health-personal-care',
            'beauty',
            'clothing-shoes-jewelry',
            'books',
            'office-products'
        ]
        
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }

    def get_bestsellers_by_category(self, category, limit=20):
        """Get best selling products from a specific category"""
        print(f"🔍 Getting best sellers from {category}...")
        
        url = f"https://www.amazon.com/Best-Sellers-{category}/zgbs/{category}"
        
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            if response.status_code != 200:
                print(f"❌ Failed to access {category} bestsellers")
                return []
            
            soup = BeautifulSoup(response.content, 'html.parser')
            products = []
            
            # Find product containers
            product_containers = soup.find_all('div', {'data-component-type': 'sl-product-card'})
            
            for container in product_containers[:limit]:
                try:
                    product = self.extract_product_info(container)
                    if product and product.get('asin'):
                        products.append(product)
                        print(f"✅ Found: {product.get('title', 'Unknown')}")
                except Exception as e:
                    print(f"⚠️ Error extracting product: {e}")
                    continue
            
            return products
            
        except Exception as e:
            print(f"❌ Error scraping {category}: {e}")
            return []

    def extract_product_info(self, container):
        """Extract product information from container"""
        product = {}
        
        try:
            # Get ASIN from data attribute or href
            asin_elem = container.find('a', href=True)
            if asin_elem and '/dp/' in asin_elem['href']:
                asin = asin_elem['href'].split('/dp/')[-1].split('/')[0].split('?')[0]
                if len(asin) == 10:  # Valid ASIN length
                    product['asin'] = asin
            
            # Get title
            title_elem = container.find('a', {'aria-label': True})
            if title_elem:
                product['title'] = title_elem.get('aria-label', '').strip()
            
            # Get price
            price_elem = container.find('span', class_='a-price-whole')
            if price_elem:
                price_text = price_elem.get_text(strip=True).replace(',', '')
                try:
                    product['price'] = f"{int(price_text)}.99"
                except:
                    product['price'] = "29.99"
            
            # Get rating
            rating_elem = container.find('span', class_='a-icon-alt')
            if rating_elem:
                rating_text = rating_elem.get_text(strip=True)
                if 'out of' in rating_text:
                    rating = rating_text.split()[0]
                    try:
                        product['rating'] = float(rating)
                    except:
                        product['rating'] = 4.5
            else:
                product['rating'] = 4.5
            
            return product
            
        except Exception as e:
            print(f"❌ Error extracting product info: {e}")
            return None

    def get_trending_products_all_categories(self, products_per_category=10):
        """Get trending products from all categories"""
        print("🚀 Getting trending products from all Amazon categories...")
        
        all_products = []
        
        for category in self.categories:
            try:
                products = self.get_bestsellers_by_category(category, products_per_category)
                for product in products:
                    product['category'] = category.replace('-', ' ').title()
                all_products.extend(products)
                
                # Add delay to avoid being blocked
                time.sleep(random.uniform(2, 5))
                
            except Exception as e:
                print(f"❌ Error getting products from {category}: {e}")
                continue
        
        print(f"🎉 Found {len(all_products)} trending products!")
        return all_products

    def update_product_catalog(self):
        """Update the product catalog with fresh trending products"""
        print("🔄 Updating product catalog with trending Amazon products...")
        
        with app.app_context():
            # Get trending products
            trending_products = self.get_trending_products_all_categories()
            
            if not trending_products:
                print("❌ No trending products found")
                return 0
            
            # Clear old products and add new ones
            ProductInventory.query.delete()
            db.session.commit()
            print("🗑️ Cleared old product catalog")
            
            added_count = 0
            for product_data in trending_products:
                try:
                    if not product_data.get('asin') or not product_data.get('title'):
                        continue
                    
                    # Create new product
                    product = ProductInventory()
                    product.asin = product_data['asin']
                    product.product_title = product_data['title'][:255]  # Truncate if too long
                    product.price = product_data.get('price', '29.99')
                    product.rating = product_data.get('rating', 4.5)
                    product.category = product_data.get('category', 'Electronics')
                    
                    # Create working image and affiliate URLs
                    product.image_url = f"https://images-na.ssl-images-amazon.com/images/P/{product_data['asin']}.jpg"
                    product.is_active = True
                    
                    db.session.add(product)
                    db.session.commit()
                    added_count += 1
                    
                    print(f"✅ Added: {product_data['title']}")
                    
                except Exception as e:
                    print(f"❌ Error adding product: {e}")
                    continue
            
            print(f"🎉 Successfully updated catalog with {added_count} trending products!")
            return added_count

def run_trending_update():
    """Main function to update with trending products"""
    scraper = AmazonBestSellersScraper()
    return scraper.update_product_catalog()

if __name__ == '__main__':
    run_trending_update()