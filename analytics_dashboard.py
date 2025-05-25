"""
Analytics Dashboard - Track campaign performance and revenue
"""
from datetime import datetime, timedelta
from sqlalchemy import func
from app import db
from models import Post, User, Campaign, ProductInventory


class AnalyticsDashboard:
    def __init__(self, user=None):
        self.user = user
    
    def get_user_analytics(self, days=30):
        """Get comprehensive analytics for user"""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        # Get user's posts in date range
        posts = Post.query.filter(
            Post.user_id == self.user.id,
            Post.created_at >= start_date
        ).all()
        
        total_posts = len(posts)
        total_clicks = sum(post.clicks for post in posts)
        total_impressions = sum(post.impressions for post in posts)
        estimated_revenue = sum(post.revenue_estimated for post in posts)
        
        # Platform breakdown
        platform_stats = {
            'discord': {'posts': 0, 'clicks': 0},
            'telegram': {'posts': 0, 'clicks': 0},
            'slack': {'posts': 0, 'clicks': 0},
            'email': {'posts': 0, 'clicks': 0}
        }
        
        for post in posts:
            if post.posted_to_discord:
                platform_stats['discord']['posts'] += 1
                platform_stats['discord']['clicks'] += post.clicks
            if post.posted_to_telegram:
                platform_stats['telegram']['posts'] += 1
                platform_stats['telegram']['clicks'] += post.clicks
            if post.posted_to_slack:
                platform_stats['slack']['posts'] += 1
                platform_stats['slack']['clicks'] += post.clicks
            if post.posted_to_email:
                platform_stats['email']['posts'] += 1
                platform_stats['email']['clicks'] += post.clicks
        
        # Top performing products
        top_products = sorted(posts, key=lambda x: x.clicks, reverse=True)[:5]
        
        # Daily stats for chart
        daily_stats = self._get_daily_stats(start_date, end_date)
        
        return {
            'total_posts': total_posts,
            'total_clicks': total_clicks,
            'total_impressions': total_impressions,
            'estimated_revenue': estimated_revenue,
            'click_through_rate': (total_clicks / total_impressions * 100) if total_impressions > 0 else 0,
            'avg_revenue_per_post': estimated_revenue / total_posts if total_posts > 0 else 0,
            'platform_stats': platform_stats,
            'top_products': top_products,
            'daily_stats': daily_stats,
            'conversion_rate': sum(post.conversion_rate for post in posts) / total_posts if total_posts > 0 else 0
        }
    
    def get_admin_analytics(self):
        """Get platform-wide analytics for admin"""
        # Total users by tier
        user_counts = db.session.query(
            User.subscription_tier,
            func.count(User.id)
        ).group_by(User.subscription_tier).all()
        
        # Total posts last 30 days
        thirty_days_ago = datetime.now() - timedelta(days=30)
        recent_posts = Post.query.filter(Post.created_at >= thirty_days_ago).count()
        
        # Total revenue estimate
        total_revenue = db.session.query(func.sum(Post.revenue_estimated)).scalar() or 0
        
        # Most popular products
        popular_products = db.session.query(
            ProductInventory.product_title,
            ProductInventory.times_promoted,
            ProductInventory.total_clicks
        ).order_by(ProductInventory.times_promoted.desc()).limit(10).all()
        
        # Platform usage
        platform_usage = {
            'discord': Post.query.filter(Post.posted_to_discord == True).count(),
            'telegram': Post.query.filter(Post.posted_to_telegram == True).count(),
            'slack': Post.query.filter(Post.posted_to_slack == True).count(),
            'email': Post.query.filter(Post.posted_to_email == True).count()
        }
        
        # Growth metrics
        total_users = User.query.count()
        new_users_30d = User.query.filter(User.created_at >= thirty_days_ago).count()
        
        return {
            'user_counts': dict(user_counts),
            'total_users': total_users,
            'new_users_30d': new_users_30d,
            'recent_posts': recent_posts,
            'total_revenue': total_revenue,
            'popular_products': popular_products,
            'platform_usage': platform_usage,
            'growth_rate': (new_users_30d / total_users * 100) if total_users > 0 else 0
        }
    
    def _get_daily_stats(self, start_date, end_date):
        """Get daily statistics for charts"""
        daily_stats = []
        current_date = start_date
        
        while current_date <= end_date:
            next_date = current_date + timedelta(days=1)
            
            day_posts = Post.query.filter(
                Post.user_id == self.user.id,
                Post.created_at >= current_date,
                Post.created_at < next_date
            ).all()
            
            daily_stats.append({
                'date': current_date.strftime('%Y-%m-%d'),
                'posts': len(day_posts),
                'clicks': sum(post.clicks for post in day_posts),
                'revenue': sum(post.revenue_estimated for post in day_posts)
            })
            
            current_date = next_date
        
        return daily_stats
    
    def get_product_performance(self, limit=20):
        """Get top performing products for user"""
        if not self.user:
            return []
        
        posts = Post.query.filter(Post.user_id == self.user.id).all()
        
        # Group by ASIN and aggregate stats
        product_stats = {}
        for post in posts:
            asin = post.asin or post.product_title
            if asin not in product_stats:
                product_stats[asin] = {
                    'title': post.product_title,
                    'posts': 0,
                    'clicks': 0,
                    'revenue': 0,
                    'conversion_rate': 0,
                    'category': post.category
                }
            
            product_stats[asin]['posts'] += 1
            product_stats[asin]['clicks'] += post.clicks
            product_stats[asin]['revenue'] += post.revenue_estimated
        
        # Calculate conversion rates
        for asin, stats in product_stats.items():
            if stats['clicks'] > 0:
                stats['conversion_rate'] = (stats['revenue'] / stats['clicks']) * 100
        
        # Sort by revenue and return top performers
        sorted_products = sorted(
            product_stats.items(),
            key=lambda x: x[1]['revenue'],
            reverse=True
        )
        
        return sorted_products[:limit]