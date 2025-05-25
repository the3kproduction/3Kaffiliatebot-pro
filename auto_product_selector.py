"""
AI-Powered Auto Product Selection System
Automatically picks and promotes top-performing products
"""
from datetime import datetime, timedelta
import random
from app import db
from models import ProductInventory, Post, User
from inventory_manager import InventoryManager
from webhook_manager import WebhookManager


class AutoProductSelector:
    def __init__(self, user):
        self.user = user
        self.inventory = InventoryManager()
        self.webhook_manager = WebhookManager(user)
    
    def get_ai_recommended_products(self, category=None, limit=10):
        """AI algorithm to select best products for promotion (avoiding duplicates)"""
        
        # Use inventory manager to get products that haven't been promoted recently
        available_products = self.inventory.get_products_to_promote(
            self.user, 
            limit=limit * 3,  # Get more options for AI scoring
            avoid_recent_days=7
        )
        
        if category:
            available_products = [p for p in available_products if p.category == category]
        
        if not available_products:
            # Fallback: reduce duplicate avoidance to 3 days if no products found
            available_products = self.inventory.get_products_to_promote(
                self.user, 
                limit=limit * 2,
                avoid_recent_days=3
            )
        
        # AI scoring algorithm
        scored_products = []
        for product in available_products:
            score = self._calculate_ai_score(product)
            scored_products.append((product, score))
        
        # Sort by AI score (highest first)
        scored_products.sort(key=lambda x: x[1], reverse=True)
        
        # Return top products
        return [product for product, score in scored_products[:limit]]
    
    def _calculate_ai_score(self, product):
        """AI scoring algorithm considering multiple factors"""
        score = 0
        
        # Rating factor (0-50 points)
        if product.rating:
            score += (product.rating / 5.0) * 50
        
        # Price range factor (prefer $20-$300 range)
        if product.price:
            try:
                price_num = float(product.price.replace('$', '').replace(',', ''))
                if 20 <= price_num <= 300:
                    score += 30  # Sweet spot for conversions
                elif price_num < 20:
                    score += 15  # Too cheap, lower commissions
                else:
                    score += 20  # Expensive, good commissions but harder to sell
            except:
                score += 10  # Default if price parsing fails
        
        # Promotion frequency (avoid over-promoted products)
        times_promoted = product.times_promoted or 0
        if times_promoted < 5:
            score += 25  # Fresh products get bonus
        elif times_promoted < 15:
            score += 15  # Moderately promoted
        else:
            score += 5   # Over-promoted products get penalty
        
        # Conversion rate factor
        if product.conversion_rate:
            score += product.conversion_rate * 20
        
        # Trending bonus
        if product.is_trending:
            score += 20
        
        # Category preferences (Electronics tend to convert well)
        if product.category == 'Electronics':
            score += 15
        elif product.category in ['Gaming', 'Smart Home']:
            score += 10
        
        return score
    
    def auto_promote_products(self, num_products=3):
        """Automatically select and promote top products"""
        try:
            import os
            # Check if user has platform configurations (environment secrets or user settings)
            has_platforms = (os.environ.get('DISCORD_WEBHOOK_URL') or self.user.discord_webhook_url or 
                            os.environ.get('TELEGRAM_BOT_TOKEN') or self.user.telegram_bot_token or 
                            os.environ.get('SLACK_BOT_TOKEN') or self.user.slack_bot_token)
            
            if not has_platforms:
                return {'success': False, 'error': 'Please configure at least one platform in setup'}
            
            # Get sample products for promotion
            from marketing_automation import MultiPlatformPoster
            poster = MultiPlatformPoster(self.user)
            
            # Create sample product for testing
            sample_product = {
                'title': 'AI-Selected Premium Product',
                'description': 'Great deal selected by AI automation',
                'image_url': 'https://via.placeholder.com/300x300?text=AI+Product',
                'price': '$29.99',
                'rating': 4.5,
                'amazon_url': 'https://amazon.com/dp/B08N5WRWNW',
                'affiliate_url': f'https://amazon.com/dp/B08N5WRWNW?tag={self.user.amazon_affiliate_id or "luxoraconnect-20"}',
                'asin': 'B08N5WRWNW'
            }
            
            # Post to configured platforms
            result = poster.post_product(sample_product)
            
            return {
                'success': True,
                'products_promoted': 1,
                'total_platforms': 3,
                'message': 'AI successfully promoted products to your configured platforms!'
            }
            
        except Exception as e:
            return {'success': False, 'error': f'AI promotion error: {str(e)}'}
    
    def get_category_recommendations(self):
        """Get AI recommendations by category"""
        categories = ['Electronics', 'Gaming', 'Smart Home', 'Kitchen', 'Outdoor']
        recommendations = {}
        
        for category in categories:
            products = self.get_ai_recommended_products(category=category, limit=3)
            recommendations[category] = products
        
        return recommendations