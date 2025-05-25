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
        
        # Check if user has webhooks configured
        webhooks = self.webhook_manager.get_user_webhooks()
        if not webhooks:
            return {'success': False, 'error': 'No webhooks configured'}
        
        # Check posting frequency limits
        from subscription_manager import SubscriptionManager
        if not SubscriptionManager.can_user_post(self.user):
            return {'success': False, 'error': 'Posting frequency limit reached'}
        
        # Get AI-recommended products
        recommended_products = self.get_ai_recommended_products(limit=num_products * 2)
        
        # Filter out recently promoted products by this user
        try:
            recent_posts = db.session.query(Post).filter(
                Post.user_id == self.user.id,
                Post.created_at >= datetime.now() - timedelta(hours=24)
            ).all()
            
            recent_asins = [post.asin for post in recent_posts if post.asin]
            
            available_products = [
                p for p in recommended_products 
                if p.asin not in recent_asins
            ][:num_products]
        except Exception:
            # Fallback: just use the recommended products
            available_products = recommended_products[:num_products]
        
        if not available_products:
            return {'success': False, 'error': 'No suitable products available'}
        
        # Promote selected products
        promoted_products = []
        total_platforms = 0
        
        for product in available_products:
            # Create affiliate URL
            affiliate_url = f"https://amazon.com/dp/{product.asin}?tag={self.user.amazon_affiliate_id}"
            
            # Post to all webhooks
            platforms_posted = 0
            for webhook in webhooks:
                result = self.webhook_manager.post_to_webhook(webhook.id, {
                    'title': product.product_title,
                    'price': product.price,
                    'rating': product.rating,
                    'affiliate_url': affiliate_url,
                    'image_url': product.image_url
                })
                
                if result['success']:
                    platforms_posted += 1
            
            if platforms_posted > 0:
                # Record the post
                new_post = Post(
                    user_id=self.user.id,
                    product_title=product.product_title,
                    product_description=f"AI-selected top product: {product.product_title}",
                    product_image_url=product.image_url,
                    amazon_url=f"https://amazon.com/dp/{product.asin}",
                    affiliate_url=affiliate_url,
                    price=product.price,
                    rating=product.rating,
                    category=product.category,
                    asin=product.asin,
                    posted_to_discord=any(w.platform == 'discord' for w in webhooks),
                    posted_to_slack=any(w.platform == 'slack' for w in webhooks),
                    posted_to_telegram=any(w.platform == 'telegram' for w in webhooks)
                )
                db.session.add(new_post)
                
                # Update product stats
                self.inventory.mark_product_promoted(product.asin, self.user.id)
                
                promoted_products.append({
                    'title': product.product_title,
                    'price': product.price,
                    'platforms': platforms_posted
                })
                total_platforms += platforms_posted
        
        db.session.commit()
        
        return {
            'success': True,
            'products_promoted': len(promoted_products),
            'total_platforms': total_platforms,
            'products': promoted_products
        }
    
    def get_category_recommendations(self):
        """Get AI recommendations by category"""
        categories = ['Electronics', 'Gaming', 'Smart Home', 'Kitchen', 'Outdoor']
        recommendations = {}
        
        for category in categories:
            products = self.get_ai_recommended_products(category=category, limit=3)
            recommendations[category] = products
        
        return recommendations