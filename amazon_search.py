"""
Amazon Product Search System
Search and retrieve products directly from Amazon
"""
import requests
from bs4 import BeautifulSoup
import re
import time
import random
from urllib.parse import quote_plus
from models import ProductInventory
from app import db


class AmazonSearcher:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
    
    def search_products(self, query, limit=20):
        """Search Amazon for products based on query"""
        try:
            # Format search URL
            search_url = f"https://www.amazon.com/s?k={quote_plus(query)}&ref=sr_pg_1"
            
            # Add random delay to avoid rate limiting
            time.sleep(random.uniform(1, 3))
            
            response = requests.get(search_url, headers=self.headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find product containers
            products = []
            product_containers = soup.find_all('div', {'data-component-type': 's-search-result'})
            
            for container in product_containers[:limit]:
                product_data = self._extract_product_data(container)
                if product_data and product_data.get('asin'):
                    products.append(product_data)
            
            return products
            
        except Exception as e:
            print(f"Error searching Amazon: {e}")
            return []
    
    def _extract_product_data(self, container):
        """Extract product information from search result container"""
        try:
            product = {}
            
            # Extract ASIN
            asin = container.get('data-asin')
            if not asin:
                return None
            product['asin'] = asin
            
            # Extract title
            title_elem = container.find('h2', class_='a-size-mini') or container.find('span', class_='a-size-medium')
            if title_elem:
                title_link = title_elem.find('a')
                if title_link:
                    product['title'] = title_link.get_text(strip=True)
            
            # Extract price
            price_container = container.find('span', class_='a-price')
            if price_container:
                price_elem = price_container.find('span', class_='a-offscreen')
                if price_elem:
                    product['price'] = price_elem.get_text(strip=True)
            
            # Extract rating
            rating_elem = container.find('span', class_='a-icon-alt')
            if rating_elem:
                rating_text = rating_elem.get_text()
                rating_match = re.search(r'(\d+\.?\d*) out of', rating_text)
                if rating_match:
                    product['rating'] = float(rating_match.group(1))
            
            # Extract image
            img_elem = container.find('img', class_='s-image')
            if img_elem:
                product['image_url'] = img_elem.get('src', '')
            
            # Set category based on search context
            product['category'] = 'Electronics'  # Default category
            
            return product
            
        except Exception as e:
            print(f"Error extracting product data: {e}")
            return None
    
    def add_search_results_to_inventory(self, products):
        """Add search results to product inventory"""
        added_count = 0
        
        for product_data in products:
            try:
                # Check if product already exists
                existing = ProductInventory.query.filter_by(asin=product_data['asin']).first()
                
                if not existing:
                    # Create new product
                    new_product = ProductInventory(
                        asin=product_data['asin'],
                        product_title=product_data.get('title', 'Unknown Product'),
                        category=product_data.get('category', 'Electronics'),
                        price=product_data.get('price', ''),
                        rating=product_data.get('rating', 0.0),
                        image_url=product_data.get('image_url', ''),
                        is_active=True,
                        is_trending=False
                    )
                    db.session.add(new_product)
                    added_count += 1
                
            except Exception as e:
                print(f"Error adding product to inventory: {e}")
                continue
        
        try:
            db.session.commit()
            return added_count
        except Exception as e:
            print(f"Error committing to database: {e}")
            db.session.rollback()
            return 0
    
    def get_trending_searches(self):
        """Get popular search terms for suggestions"""
        trending = [
            "wireless earbuds", "smart watch", "laptop", "phone case",
            "bluetooth speaker", "gaming headset", "tablet", "fitness tracker",
            "portable charger", "wireless mouse", "keyboard", "webcam",
            "smart home", "coffee maker", "air fryer", "vacuum cleaner"
        ]
        return trending
    
    def search_and_add_to_inventory(self, query, limit=20):
        """Search for products and automatically add them to inventory"""
        print(f"Searching Amazon for: {query}")
        
        # Search for products
        search_results = self.search_products(query, limit)
        
        if not search_results:
            return {
                'success': False,
                'message': f'No products found for "{query}"',
                'products_added': 0
            }
        
        # Add to inventory
        added_count = self.add_search_results_to_inventory(search_results)
        
        return {
            'success': True,
            'message': f'Found {len(search_results)} products, added {added_count} new ones',
            'products_added': added_count,
            'total_found': len(search_results)
        }