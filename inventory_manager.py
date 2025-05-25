"""
Product Inventory Manager - Track products and avoid duplicates
"""
from datetime import datetime, timedelta
from app import db
from models import ProductInventory, Post
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
    
    def get_products_to_promote(self, user, limit=10):
        """Get products that haven't been promoted recently by this user"""
        # Get user's recent posts (last 7 days)
        recent_posts = Post.query.filter(
            Post.user_id == user.id,
            Post.created_at >= datetime.now() - timedelta(days=7)
        ).all()
        
        recent_asins = [post.asin for post in recent_posts if post.asin]
        
        # Get products not recently promoted
        query = ProductInventory.query.filter(
            ProductInventory.is_active == True
        )
        
        if recent_asins:
            query = query.filter(~ProductInventory.asin.in_(recent_asins))
        
        return query.order_by(ProductInventory.conversion_rate.desc()).limit(limit).all()
    
    def mark_product_promoted(self, asin, user_id):
        """Mark a product as promoted"""
        product = ProductInventory.query.filter_by(asin=asin).first()
        if product:
            product.times_promoted += 1
            product.last_promoted = datetime.now()
            db.session.commit()
    
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