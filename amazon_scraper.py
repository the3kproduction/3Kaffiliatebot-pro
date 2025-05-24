import requests
import json
import re
from bs4 import BeautifulSoup
from urllib.parse import urljoin, quote
import logging

logger = logging.getLogger(__name__)

class AmazonProductScraper:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
    
    def extract_asin_from_affiliate_link(self, affiliate_link):
        """Extract ASIN from affiliate link like amzn.to/44TOVc2"""
        try:
            # Follow the redirect to get the actual Amazon URL
            response = requests.get(affiliate_link, headers=self.headers, allow_redirects=True)
            final_url = response.url
            
            # Extract ASIN from the final URL
            asin_match = re.search(r'/dp/([A-Z0-9]{10})', final_url)
            if asin_match:
                return asin_match.group(1)
            
            # Alternative pattern
            asin_match = re.search(r'/gp/product/([A-Z0-9]{10})', final_url)
            if asin_match:
                return asin_match.group(1)
                
            return None
        except Exception as e:
            logger.error(f"Error extracting ASIN: {e}")
            return None
    
    def get_top_products_by_category(self, category="Electronics", limit=10):
        """Get top products from Amazon's best sellers in a category"""
        try:
            # Amazon Best Sellers URLs by category
            category_urls = {
                "Electronics": "https://www.amazon.com/Best-Sellers-Electronics/zgbs/electronics",
                "Books": "https://www.amazon.com/Best-Sellers-Books/zgbs/books",
                "Home": "https://www.amazon.com/Best-Sellers-Home-Kitchen/zgbs/home-garden",
                "Fashion": "https://www.amazon.com/Best-Sellers-Clothing-Shoes-Jewelry/zgbs/fashion",
                "Health": "https://www.amazon.com/Best-Sellers-Health-Personal-Care/zgbs/hpc",
                "Sports": "https://www.amazon.com/Best-Sellers-Sports-Outdoors/zgbs/sporting-goods",
                "Tools": "https://www.amazon.com/Best-Sellers-Tools-Home-Improvement/zgbs/hi",
                "Toys": "https://www.amazon.com/Best-Sellers-Toys-Games/zgbs/toys-and-games"
            }
            
            url = category_urls.get(category, category_urls["Electronics"])
            
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            products = []
            
            # Find product containers in best sellers page
            product_containers = soup.find_all('div', {'class': re.compile('zg-grid-general-faceout')})
            
            for container in product_containers[:limit]:
                try:
                    product = self.extract_product_info(container)
                    if product:
                        products.append(product)
                except Exception as e:
                    logger.error(f"Error extracting product: {e}")
                    continue
            
            return products
            
        except Exception as e:
            logger.error(f"Error getting top products: {e}")
            return []
    
    def extract_product_info(self, container):
        """Extract product information from container"""
        try:
            # Product title
            title_elem = container.find('div', class_='p13n-sc-truncate')
            if not title_elem:
                title_elem = container.find('a', class_='a-link-normal')
            title = title_elem.get_text(strip=True) if title_elem else "Product Title"
            
            # Product URL
            link_elem = container.find('a', class_='a-link-normal')
            if link_elem and link_elem.get('href'):
                product_url = urljoin('https://www.amazon.com', link_elem['href'])
            else:
                return None
            
            # Extract ASIN from URL
            asin_match = re.search(r'/dp/([A-Z0-9]{10})', product_url)
            if not asin_match:
                return None
            asin = asin_match.group(1)
            
            # Product image
            img_elem = container.find('img')
            image_url = img_elem.get('src') if img_elem else ""
            
            # Price
            price_elem = container.find('span', class_='p13n-sc-price')
            if not price_elem:
                price_elem = container.find('span', class_='a-price-whole')
            price = price_elem.get_text(strip=True) if price_elem else "Price not available"
            
            # Rating
            rating_elem = container.find('span', class_='a-icon-alt')
            rating = 0.0
            if rating_elem:
                rating_text = rating_elem.get_text()
                rating_match = re.search(r'(\d+\.?\d*)', rating_text)
                if rating_match:
                    rating = float(rating_match.group(1))
            
            return {
                'title': title[:200],  # Limit title length
                'asin': asin,
                'url': product_url,
                'image': image_url,
                'price': price,
                'rating': rating,
                'description': f"Top-rated {title} from Amazon's best sellers"
            }
            
        except Exception as e:
            logger.error(f"Error extracting product info: {e}")
            return None
    
    def create_affiliate_url(self, asin, affiliate_tag):
        """Create affiliate URL from ASIN and affiliate tag"""
        try:
            # Extract the tag from affiliate link like amzn.to/44TOVc2
            # This would need to be mapped to actual affiliate tag
            base_url = f"https://www.amazon.com/dp/{asin}"
            
            # If user provides their full affiliate tag format
            if affiliate_tag:
                return f"{base_url}?tag={affiliate_tag}"
            
            return base_url
            
        except Exception as e:
            logger.error(f"Error creating affiliate URL: {e}")
            return f"https://www.amazon.com/dp/{asin}"
    
    def get_trending_products(self, limit=10):
        """Get trending products from Amazon's main page"""
        try:
            response = requests.get("https://www.amazon.com", headers=self.headers)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            products = []
            
            # Look for product cards on homepage
            product_links = soup.find_all('a', href=re.compile(r'/dp/[A-Z0-9]{10}'))
            
            seen_asins = set()
            for link in product_links[:limit * 2]:  # Get extra to filter duplicates
                try:
                    asin_match = re.search(r'/dp/([A-Z0-9]{10})', link['href'])
                    if asin_match and asin_match.group(1) not in seen_asins:
                        asin = asin_match.group(1)
                        seen_asins.add(asin)
                        
                        # Get product info from the link context
                        img = link.find('img')
                        title = img.get('alt') if img else link.get_text(strip=True)
                        image_url = img.get('src') if img else ""
                        
                        if title and len(title) > 5:  # Valid title
                            products.append({
                                'title': title[:200],
                                'asin': asin,
                                'url': urljoin('https://www.amazon.com', link['href']),
                                'image': image_url,
                                'price': "Check Amazon for price",
                                'rating': 4.5,  # Default rating
                                'description': f"Trending product: {title}"
                            })
                            
                        if len(products) >= limit:
                            break
                            
                except Exception as e:
                    continue
            
            return products
            
        except Exception as e:
            logger.error(f"Error getting trending products: {e}")
            return []