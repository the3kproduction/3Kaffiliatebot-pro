"""
Automated Product Posting Service
Automatically posts products for users based on their campaign settings
"""
import os
import random
import time
from datetime import datetime, timedelta
from working_app import db, User, Campaign, ProductInventory, ProductPromotion
from marketing_automation import MultiPlatformPoster
from inventory_manager import InventoryManager

class AutomatedPostingService:
    def __init__(self):
        self.inventory_manager = InventoryManager()
        
    def get_user_posting_schedule(self, user):
        """Get how often user should post based on subscription tier"""
        tier_limits = {
            'free': 2,      # 2 posts per day
            'premium': 8,   # 8 posts per day  
            'pro': 24       # 24 posts per day
        }
        
        posts_per_day = tier_limits.get(user.subscription_tier, 2)
        hours_between_posts = 24 / posts_per_day if posts_per_day > 0 else 12
        
        return {
            'posts_per_day': posts_per_day,
            'hours_between_posts': hours_between_posts,
            'can_post_now': self.can_user_post_now(user, hours_between_posts)
        }
    
    def can_user_post_now(self, user, hours_between_posts):
        """Check if enough time has passed since last post"""
        last_promotion = ProductPromotion.query.filter_by(
            user_id=user.id
        ).order_by(ProductPromotion.promoted_at.desc()).first()
        
        if not last_promotion:
            return True
            
        time_since_last = datetime.now() - last_promotion.promoted_at
        required_gap = timedelta(hours=hours_between_posts)
        
        return time_since_last >= required_gap
    
    def auto_post_for_user(self, user):
        """Automatically post a product for a specific user"""
        schedule = self.get_user_posting_schedule(user)
        
        if not schedule['can_post_now']:
            return {
                'success': False,
                'message': f'Must wait {schedule["hours_between_posts"]:.1f} hours between posts'
            }
        
        # Get active campaigns for user
        active_campaigns = Campaign.query.filter_by(
            user_id=user.id,
            status='active'
        ).all()
        
        if not active_campaigns:
            return {
                'success': False,
                'message': 'No active campaigns found. Create a campaign first.'
            }
        
        # Select random campaign
        campaign = random.choice(active_campaigns)
        
        # Get products to promote (avoiding recent duplicates)
        products = self.inventory_manager.get_products_to_promote(
            user, 
            limit=10, 
            avoid_recent_days=7
        )
        
        if not products:
            return {
                'success': False,
                'message': 'No products available for promotion right now'
            }
        
        # Select best product using AI scoring
        selected_product = self.select_best_product(products, campaign)
        
        # Post to user's configured platforms
        poster = MultiPlatformPoster(user)
        result = poster.post_product(selected_product)
        
        if result['success']:
            # Mark product as promoted
            self.inventory_manager.mark_product_promoted(
                selected_product.asin,
                user.id,
                platform='auto',
                post_id=f"auto_{int(time.time())}"
            )
            
            # Update campaign stats
            campaign.total_posts += 1
            db.session.commit()
            
            return {
                'success': True,
                'message': f'Posted {selected_product.product_title} to configured platforms',
                'product': selected_product.product_title,
                'campaign': campaign.name
            }
        else:
            return {
                'success': False,
                'message': f'Failed to post: {result.get("error", "Unknown error")}'
            }
    
    def select_best_product(self, products, campaign):
        """AI algorithm to select the best product for posting"""
        scored_products = []
        
        for product in products:
            score = 0
            
            # Price range scoring (mid-range products often perform better)
            try:
                price = float(product.price.replace('$', '').replace(',', ''))
                if 20 <= price <= 100:
                    score += 30
                elif 10 <= price <= 200:
                    score += 20
                else:
                    score += 10
            except:
                score += 15  # Default if price parsing fails
            
            # Rating scoring
            if product.rating:
                if product.rating >= 4.5:
                    score += 25
                elif product.rating >= 4.0:
                    score += 20
                elif product.rating >= 3.5:
                    score += 15
                else:
                    score += 10
            
            # Category matching with campaign
            if campaign.category and product.category:
                if campaign.category.lower() in product.category.lower():
                    score += 20
            
            # Random factor for variety
            score += random.randint(1, 15)
            
            scored_products.append((product, score))
        
        # Sort by score and return best product
        scored_products.sort(key=lambda x: x[1], reverse=True)
        return scored_products[0][0]
    
    def run_automated_posting_cycle(self):
        """Run one cycle of automated posting for all eligible users"""
        users = User.query.filter(
            User.subscription_tier.in_(['free', 'premium', 'pro'])
        ).all()
        
        results = []
        
        for user in users:
            try:
                result = self.auto_post_for_user(user)
                results.append({
                    'user': user.username or user.email,
                    'result': result
                })
            except Exception as e:
                results.append({
                    'user': user.username or user.email,
                    'result': {
                        'success': False,
                        'message': f'Error: {str(e)}'
                    }
                })
        
        return results

def run_posting_service():
    """Main function to run the automated posting service"""
    service = AutomatedPostingService()
    results = service.run_automated_posting_cycle()
    
    print(f"Automated posting cycle completed at {datetime.now()}")
    for result in results:
        status = "✓" if result['result']['success'] else "✗"
        print(f"{status} {result['user']}: {result['result']['message']}")
    
    return results

if __name__ == "__main__":
    run_posting_service()