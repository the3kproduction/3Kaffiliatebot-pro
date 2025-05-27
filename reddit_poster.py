"""
Reddit Posting Module for Affiliate Marketing
Posts products to relevant Reddit communities
"""
import os
import requests
import time
from datetime import datetime

class RedditPoster:
    def __init__(self):
        self.client_id = os.environ.get('REDDIT_CLIENT_ID')
        self.client_secret = os.environ.get('REDDIT_CLIENT_SECRET')
        self.username = os.environ.get('REDDIT_EMAIL')  # Using email as username
        self.password = os.environ.get('REDDIT_PASSWORD')
        self.access_token = None
        self.user_agent = 'AffiliateBot Pro v1.0'
        
    def authenticate(self):
        """Get Reddit API access token"""
        try:
            auth = requests.auth.HTTPBasicAuth(self.client_id, self.client_secret)
            data = {
                'grant_type': 'password',
                'username': self.username,
                'password': self.password
            }
            headers = {'User-Agent': self.user_agent}
            
            response = requests.post('https://www.reddit.com/api/v1/access_token',
                                   auth=auth, data=data, headers=headers)
            
            if response.status_code == 200:
                token_data = response.json()
                self.access_token = token_data.get('access_token')
                return True
            else:
                print(f"Reddit auth failed: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"Reddit authentication error: {e}")
            return False
    
    def post_to_subreddit(self, product, subreddit='deals'):
        """Post product to a specific subreddit"""
        if not self.access_token:
            if not self.authenticate():
                return False
        
        try:
            headers = {
                'Authorization': f'bearer {self.access_token}',
                'User-Agent': self.user_agent
            }
            
            # Create post title and content
            title = f"🔥 Great Deal: {product.get('name', 'Amazing Product')} - {product.get('price', 'Check Price')}"
            text = f"""
Check out this amazing deal I found!

**{product.get('name', 'Product')}**
Price: {product.get('price', 'See Amazon')}
Rating: {'⭐' * int(float(product.get('rating', 4.5)))}

{product.get('description', 'Great quality product with excellent reviews!')}

[🛒 Get it on Amazon]({product.get('affiliate_url', product.get('url', '#'))})

*This post contains affiliate links. I may earn a commission if you purchase through these links.*
"""
            
            data = {
                'sr': subreddit,
                'kind': 'self',
                'title': title,
                'text': text,
                'api_type': 'json'
            }
            
            response = requests.post('https://oauth.reddit.com/api/submit',
                                   headers=headers, data=data)
            
            if response.status_code == 200:
                result = response.json()
                if result.get('json', {}).get('errors'):
                    print(f"Reddit posting errors: {result['json']['errors']}")
                    return False
                else:
                    print(f"✅ Successfully posted to r/{subreddit}")
                    return True
            else:
                print(f"Reddit post failed: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"Reddit posting error: {e}")
            return False
    
    def post_product(self, product):
        """Post product to relevant subreddits"""
        # Map product categories to appropriate subreddits
        category_subreddits = {
            'Electronics': ['deals', 'amazondeals', 'electronics'],
            'Home & Kitchen': ['deals', 'amazondeals', 'homeimprovement'],
            'Sports': ['deals', 'fitness', 'sports'],
            'Books': ['deals', 'books', 'bookdeals'],
            'Health': ['deals', 'health', 'fitness'],
            'Beauty': ['deals', 'beauty', 'skincare']
        }
        
        category = product.get('category', 'Electronics')
        subreddits = category_subreddits.get(category, ['deals'])
        
        # Post to the first suitable subreddit
        for subreddit in subreddits:
            try:
                if self.post_to_subreddit(product, subreddit):
                    return True
                time.sleep(2)  # Rate limiting
            except:
                continue
        
        return False

def test_reddit_posting():
    """Test Reddit posting functionality"""
    reddit = RedditPoster()
    
    test_product = {
        'name': 'Wireless Bluetooth Headphones',
        'price': '$49.99',
        'rating': '4.5',
        'description': 'Premium quality wireless headphones with noise cancellation.',
        'affiliate_url': 'https://amazon.com/dp/test123?tag=luxoraconnect-20',
        'category': 'Electronics'
    }
    
    print("🧪 Testing Reddit posting...")
    success = reddit.post_product(test_product)
    
    if success:
        print("✅ Reddit posting test successful!")
    else:
        print("❌ Reddit posting test failed")
    
    return success

if __name__ == '__main__':
    test_reddit_posting()