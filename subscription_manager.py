"""
Subscription Manager - Handle different posting frequencies for tiers
Free users: Every 12 hours
Premium users: Every 3 hours  
Pro users: Every 1 hour
"""

from models import User
from datetime import datetime, timedelta

class SubscriptionManager:
    
    TIER_LIMITS = {
        'free': {
            'post_frequency_hours': 12,
            'max_posts_per_day': 2,
            'platforms_allowed': ['discord', 'telegram'],
            'description': 'Free tier - Basic automation'
        },
        'premium': {
            'post_frequency_hours': 3,
            'max_posts_per_day': 8,
            'platforms_allowed': ['discord', 'telegram', 'slack', 'email'],
            'description': 'Premium tier - Full automation'
        },
        'pro': {
            'post_frequency_hours': 1,
            'max_posts_per_day': 24,
            'platforms_allowed': ['discord', 'telegram', 'slack', 'email'],
            'description': 'Pro tier - Maximum frequency'
        }
    }
    
    @classmethod
    def get_user_posting_frequency(cls, user):
        """Get posting frequency based on user's subscription tier"""
        tier = user.subscription_tier or 'free'
        return cls.TIER_LIMITS.get(tier, cls.TIER_LIMITS['free'])['post_frequency_hours']
    
    @classmethod
    def can_user_post(cls, user):
        """Check if user can post based on their tier limits"""
        tier = user.subscription_tier or 'free'
        limits = cls.TIER_LIMITS.get(tier, cls.TIER_LIMITS['free'])
        
        # Check daily post limit
        today = datetime.now().date()
        posts_today = user.posts.filter(
            user.posts.c.created_at >= today
        ).count()
        
        if posts_today >= limits['max_posts_per_day']:
            return False, f"Daily limit reached ({limits['max_posts_per_day']} posts)"
        
        # Check frequency limit
        last_post = user.posts.order_by(user.posts.c.created_at.desc()).first()
        if last_post:
            time_since_last = datetime.now() - last_post.created_at
            min_interval = timedelta(hours=limits['post_frequency_hours'])
            
            if time_since_last < min_interval:
                hours_left = (min_interval - time_since_last).total_seconds() / 3600
                return False, f"Please wait {hours_left:.1f} more hours"
        
        return True, "OK"
    
    @classmethod
    def get_allowed_platforms(cls, user):
        """Get platforms allowed for user's tier"""
        tier = user.subscription_tier or 'free'
        return cls.TIER_LIMITS.get(tier, cls.TIER_LIMITS['free'])['platforms_allowed']
    
    @classmethod
    def upgrade_user(cls, user, new_tier):
        """Upgrade user to new subscription tier"""
        if new_tier in cls.TIER_LIMITS:
            user.subscription_tier = new_tier
            return True
        return False