"""
Product Inventory Manager - Track products and avoid duplicates
"""
from datetime import datetime, timedelta
from app import db
from models import ProductInventory, Post, UserProductPromotion
from amazon_scraper import AmazonProductScraper


class InventoryManager:
    def __init__(self):
        self.scraper = AmazonProductScraper()
    
    def add_product_to_inventory(self, product_data):
        """Add a new product to inventory or update existing"""
        asin = product_data.get('asin')
        if not asin:
            return None
            
        # Check if product already exists
        existing = ProductInventory.query.filter_by(asin=asin).first()
        
        if existing:
            # Update existing product
            existing.product_title = product_data.get('title', existing.product_title)
            existing.price = product_data.get('price', existing.price)
            existing.rating = product_data.get('rating', existing.rating)
            existing.image_url = product_data.get('image_url', existing.image_url)
            existing.updated_at = datetime.now()
            db.session.commit()
            return existing
        else:
            # Create new product
            product = ProductInventory(
                asin=asin,
                product_title=product_data.get('title', ''),
                category=product_data.get('category', ''),
                price=product_data.get('price', ''),
                rating=product_data.get('rating', 0.0),
                image_url=product_data.get('image_url', '')
            )
            db.session.add(product)
            db.session.commit()
            return product
    
    def get_products_to_promote(self, user, limit=10, avoid_recent_days=7):
        """Get products that haven't been promoted recently by this user with smart filtering"""
        cutoff_date = datetime.now() - timedelta(days=avoid_recent_days)
        
        # Get ASINs that were promoted recently by this user
        recent_promotion_results = db.session.query(UserProductPromotion.asin).filter(
            UserProductPromotion.user_id == user.id,
            UserProductPromotion.promoted_at >= cutoff_date
        ).all()
        
        # Extract ASINs from results
        recent_asins = [r[0] for r in recent_promotion_results] if recent_promotion_results else []
        products = db.session.query(ProductInventory).filter(
            ProductInventory.is_active == True,
            ~ProductInventory.asin.in_(recent_asins)
        ).order_by(
            # Prioritize trending products first
            ProductInventory.is_trending.desc(),
            # Then by conversion rate (high-performing products)
            ProductInventory.conversion_rate.desc(),
            # Then by least promoted (fair rotation)
            ProductInventory.times_promoted.asc(),
            # Finally by rating
            ProductInventory.rating.desc()
        ).limit(limit).all()
        
        return products
    
    def mark_product_promoted(self, asin, user_id, platform=None, post_id=None):
        """Mark a product as promoted by a specific user"""
        # Update global product stats
        product = ProductInventory.query.filter_by(asin=asin).first()
        if product:
            product.times_promoted += 1
            product.last_promoted = datetime.now()
        
        # Record user-specific promotion to prevent duplicates
        try:
            user_promotion = UserProductPromotion(
                user_id=user_id,
                asin=asin,
                platform=platform,
                post_id=post_id,
                promoted_at=datetime.now()
            )
            db.session.add(user_promotion)
            db.session.commit()
            return True
        except Exception as e:
            # Handle duplicate promotion attempts gracefully
            db.session.rollback()
            print(f"Product {asin} already promoted by user {user_id} recently: {e}")
            return False
    
    def update_product_stats(self, asin, clicks=0, conversions=0):
        """Update product performance stats"""
        product = ProductInventory.query.filter_by(asin=asin).first()
        if product:
            product.total_clicks += clicks
            if product.total_clicks > 0:
                product.conversion_rate = conversions / product.total_clicks
            db.session.commit()
    
    def refresh_trending_products(self):
        """Refresh trending products from Amazon"""
        try:
            trending = self.scraper.get_trending_products(limit=50)
            for product_data in trending:
                self.add_product_to_inventory(product_data)
            
            # Mark products as trending
            ProductInventory.query.update({ProductInventory.is_trending: False})
            for product_data in trending:
                if product_data.get('asin'):
                    product = ProductInventory.query.filter_by(asin=product_data['asin']).first()
                    if product:
                        product.is_trending = True
            
            db.session.commit()
            return len(trending)
        except Exception as e:
            print(f"Error refreshing trending products: {e}")
            return 0
    
    def check_duplicate_promotion(self, user_id, asin, days=7):
        """Check if user has promoted this product recently"""
        cutoff_date = datetime.now() - timedelta(days=days)
        
        existing = UserProductPromotion.query.filter(
            UserProductPromotion.user_id == user_id,
            UserProductPromotion.asin == asin,
            UserProductPromotion.promoted_at >= cutoff_date
        ).first()
        
        return existing is not None
    
    def get_user_promotion_history(self, user_id, limit=50):
        """Get user's promotion history with performance data"""
        promotions = db.session.query(UserProductPromotion).join(
            ProductInventory, UserProductPromotion.asin == ProductInventory.asin
        ).filter(
            UserProductPromotion.user_id == user_id
        ).order_by(
            UserProductPromotion.promoted_at.desc()
        ).limit(limit).all()
        
        return promotions
    
    def get_best_performing_products(self, user_id=None, limit=20):
        """Get best performing products globally or for specific user"""
        if user_id:
            # Get best performing products for this specific user
            promotions = db.session.query(UserProductPromotion).join(
                ProductInventory, UserProductPromotion.asin == ProductInventory.asin
            ).filter(
                UserProductPromotion.user_id == user_id
            ).order_by(
                UserProductPromotion.revenue_generated.desc(),
                UserProductPromotion.clicks_generated.desc()
            ).limit(limit).all()
            
            return [p.product for p in promotions]
        else:
            # Get globally best performing products
            return ProductInventory.query.filter(
                ProductInventory.is_active == True
            ).order_by(
                ProductInventory.conversion_rate.desc(),
                ProductInventory.total_clicks.desc()
            ).limit(limit).all()