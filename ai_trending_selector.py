"""
AI-Powered Trending Product Selector
Uses real market data and AI to automatically select the hottest trending products
"""
import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime
from models import ProductInventory, db
from app import app

class AITrendingSelector:
    def __init__(self):
        self.trending_sources = {
            'amazon_bestsellers': 'https://www.amazon.com/gp/bestsellers/',
            'amazon_new_releases': 'https://www.amazon.com/gp/new-releases/',
            'amazon_hot_new_releases': 'https://www.amazon.com/gp/movers-and-shakers/'
        }
        
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
        }

    def get_trending_categories_data(self):
        """Get trending product data from multiple Amazon sources"""
        trending_data = {}
        
        categories = [
            'electronics', 'home-kitchen', 'sports-outdoors', 
            'health-personal-care', 'books', 'clothing-shoes-jewelry',
            'toys-games', 'automotive', 'pet-supplies', 'beauty'
        ]
        
        for category in categories:
            try:
                # Get bestsellers for this category
                url = f"https://www.amazon.com/Best-Sellers-{category}/zgbs/{category}"
                response = requests.get(url, headers=self.headers, timeout=10)
                
                if response.status_code == 200:
                    soup = BeautifulSoup(response.content, 'html.parser')
                    products = self.extract_trending_products(soup, category)
                    trending_data[category] = products
                    print(f"✅ Got {len(products)} trending products from {category}")
                
            except Exception as e:
                print(f"⚠️ Error getting data for {category}: {e}")
                continue
        
        return trending_data

    def extract_trending_products(self, soup, category):
        """Extract product data from Amazon bestsellers page"""
        products = []
        
        # Look for product containers
        product_containers = soup.find_all('div', {'data-component-type': 'sl-product-card'})[:10]
        
        for container in product_containers:
            try:
                # Extract ASIN
                link = container.find('a', href=True)
                if link and '/dp/' in link['href']:
                    asin = link['href'].split('/dp/')[-1].split('/')[0].split('?')[0]
                    if len(asin) == 10:  # Valid ASIN
                        
                        # Extract title from aria-label or text
                        title_elem = container.find('a', {'aria-label': True})
                        title = "Amazon Product"
                        if title_elem:
                            title = title_elem.get('aria-label', '').strip()
                        
                        # Extract price
                        price_elem = container.find('span', class_='a-price-whole')
                        price = "29.99"
                        if price_elem:
                            try:
                                price_val = price_elem.get_text().strip().replace(',', '')
                                price = f"{int(price_val)}.99"
                            except:
                                pass
                        
                        # Calculate AI trend score
                        trend_score = self.calculate_trend_score(container, category)
                        
                        product = {
                            'asin': asin,
                            'title': title[:200],
                            'price': price,
                            'category': category.replace('-', ' ').title(),
                            'trend_score': trend_score,
                            'rating': 4.5
                        }
                        
                        products.append(product)
                        
            except Exception as e:
                continue
        
        return products

    def calculate_trend_score(self, container, category):
        """AI algorithm to calculate how trending a product is"""
        score = 50  # Base score
        
        # Check for badges that indicate trending
        badges = container.find_all('span', class_=['a-badge', 'a-label'])
        for badge in badges:
            badge_text = badge.get_text().lower()
            if 'bestseller' in badge_text:
                score += 30
            elif 'choice' in badge_text:
                score += 25
            elif 'new' in badge_text:
                score += 20
        
        # Check rating indicators
        rating_elem = container.find('span', class_='a-icon-alt')
        if rating_elem:
            rating_text = rating_elem.get_text()
            if '4.5' in rating_text or '5' in rating_text:
                score += 15
            elif '4' in rating_text:
                score += 10
        
        # Category boost for high-converting categories
        category_boosts = {
            'electronics': 20,
            'health-personal-care': 15,
            'books': 10,
            'home-kitchen': 15
        }
        score += category_boosts.get(category, 5)
        
        return min(score, 100)  # Cap at 100

    def select_top_trending_products(self, limit=25):
        """AI selects the top trending products across all categories"""
        print("🤖 AI analyzing trending product data...")
        
        trending_data = self.get_trending_categories_data()
        all_products = []
        
        # Combine all products
        for category, products in trending_data.items():
            all_products.extend(products)
        
        # AI ranking: Sort by trend score and diversity
        ranked_products = sorted(all_products, key=lambda x: x['trend_score'], reverse=True)
        
        # Ensure category diversity
        selected_products = []
        category_counts = {}
        
        for product in ranked_products:
            category = product['category']
            if category_counts.get(category, 0) < 4:  # Max 4 per category
                selected_products.append(product)
                category_counts[category] = category_counts.get(category, 0) + 1
                
                if len(selected_products) >= limit:
                    break
        
        print(f"🎯 AI selected {len(selected_products)} top trending products")
        return selected_products

    def update_catalog_with_ai_selection(self):
        """Replace catalog with AI-selected trending products"""
        print("🚀 Updating catalog with AI-selected trending products...")
        
        with app.app_context():
            # Get AI selection
            trending_products = self.select_top_trending_products()
            
            if not trending_products:
                print("❌ No trending products found")
                return 0
            
            # Clear old products
            ProductInventory.query.delete()
            db.session.commit()
            print("🗑️ Cleared old products")
            
            # Add AI-selected products
            added_count = 0
            for product_data in trending_products:
                try:
                    product = ProductInventory()
                    product.asin = product_data['asin']
                    product.product_title = product_data['title']
                    product.price = product_data['price']
                    product.rating = product_data['rating']
                    product.category = product_data['category']
                    product.image_url = f"https://images-na.ssl-images-amazon.com/images/P/{product_data['asin']}.jpg"
                    product.is_active = True
                    
                    db.session.add(product)
                    added_count += 1
                    
                    print(f"✅ Added trending: {product_data['title']} (Score: {product_data['trend_score']})")
                    
                except Exception as e:
                    print(f"❌ Error adding product: {e}")
                    continue
            
            db.session.commit()
            print(f"🎉 Successfully added {added_count} AI-selected trending products!")
            return added_count

def run_ai_trending_update():
    """Main function for AI trending update"""
    selector = AITrendingSelector()
    return selector.update_catalog_with_ai_selection()

if __name__ == '__main__':
    run_ai_trending_update()