"""
Facebook Poster for AffiliateBot Pro
Posts affiliate products to Facebook pages/groups
"""
import os
import requests
import json

class FacebookPoster:
    def __init__(self):
        self.app_id = os.environ.get('FACEBOOK_APP_ID')
        self.app_secret = os.environ.get('FACEBOOK_APP_SECRET')
        self.access_token = os.environ.get('FACEBOOK_ACCESS_TOKEN')
        
    def post_product(self, product):
        """Post a product to Facebook"""
        try:
            # Create the post message
            message = f"""🔥 Amazing Deal Alert! 🔥

{product['title']}
💰 Price: ${product['price']}
⭐ Rating: {product.get('rating', '4.5')}/5

{product.get('description', 'Great product with excellent reviews!')}

🛒 Get yours now: {product['affiliate_url']}

#AmazonFinds #Deal #Shopping #Affiliate"""

            # Facebook Graph API endpoint for posting
            url = f"https://graph.facebook.com/v18.0/me/feed"
            
            payload = {
                'message': message,
                'link': product['affiliate_url'],
                'access_token': self.access_token
            }
            
            # If there's an image, add it
            if product.get('image_url'):
                # For Facebook, we can use the link parameter which will automatically
                # fetch the image from the Amazon URL
                pass
            
            response = requests.post(url, data=payload, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                return {
                    'success': True, 
                    'post_id': result.get('id'),
                    'message': 'Posted to Facebook successfully!'
                }
            else:
                error_data = response.json() if response.content else {}
                return {
                    'success': False, 
                    'error': f"Facebook API error: {error_data.get('error', {}).get('message', 'Unknown error')}"
                }
                
        except Exception as e:
            return {'success': False, 'error': f"Facebook posting failed: {str(e)}"}
    
    def get_pages(self):
        """Get user's Facebook pages"""
        try:
            url = f"https://graph.facebook.com/v18.0/me/accounts"
            params = {'access_token': self.access_token}
            
            response = requests.get(url, params=params, timeout=30)
            
            if response.status_code == 200:
                return response.json().get('data', [])
            else:
                return []
                
        except Exception as e:
            print(f"Error getting Facebook pages: {e}")
            return []
    
    def test_connection(self):
        """Test Facebook API connection"""
        try:
            url = f"https://graph.facebook.com/v18.0/me"
            params = {'access_token': self.access_token}
            
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                user_data = response.json()
                return {
                    'success': True, 
                    'name': user_data.get('name', 'Unknown'),
                    'id': user_data.get('id')
                }
            else:
                error_data = response.json() if response.content else {}
                return {
                    'success': False, 
                    'error': f"Facebook API error: {error_data.get('error', {}).get('message', 'Invalid access token')}"
                }
                
        except Exception as e:
            return {'success': False, 'error': f"Connection failed: {str(e)}"}

def test_facebook_posting():
    """Test Facebook posting functionality"""
    poster = FacebookPoster()
    
    # Test connection first
    connection_test = poster.test_connection()
    print(f"Facebook Connection Test: {connection_test}")
    
    if connection_test['success']:
        # Test product post
        test_product = {
            'title': 'Wireless Bluetooth Earbuds - Premium Sound Quality',
            'price': '29.99',
            'rating': '4.5',
            'description': 'High-quality wireless earbuds with noise cancellation and long battery life.',
            'affiliate_url': 'https://amzn.to/example123',
            'image_url': 'https://images-na.ssl-images-amazon.com/images/I/example.jpg'
        }
        
        result = poster.post_product(test_product)
        print(f"Facebook Post Test: {result}")
        return result
    else:
        return connection_test

if __name__ == "__main__":
    test_facebook_posting()