"""
User Management System - Grant trials and lifetime access
"""
from datetime import datetime, timedelta
from app import db
from models import User

class UserManager:
    def __init__(self):
        pass
    
    def grant_trial_access(self, user_email, trial_tier='premium', days=30):
        """Grant a user trial access to premium or pro features"""
        user = User.query.filter_by(email=user_email).first()
        if not user:
            return f"User with email {user_email} not found"
        
        # Set trial dates
        trial_start = datetime.now()
        trial_end = trial_start + timedelta(days=days)
        
        # Update user with trial access
        user.trial_start_date = trial_start
        user.trial_end_date = trial_end
        user.trial_tier = trial_tier
        user.is_trial_active = True
        user.subscription_tier = 'trial'
        
        # Set posting frequency based on trial tier
        if trial_tier == 'premium':
            user.post_frequency_hours = 3  # 8 posts per day
        elif trial_tier == 'pro':
            user.post_frequency_hours = 1  # 24 posts per day
        
        db.session.commit()
        
        return f"✅ Granted {trial_tier} trial to {user.email} for {days} days (until {trial_end.strftime('%Y-%m-%d')})"
    
    def grant_purchase_trial(self, user_email, trial_tier='premium'):
        """Grant 7-day trial before charging for paid tiers"""
        user = User.query.filter_by(email=user_email).first()
        if not user:
            return f"User with email {user_email} not found"
        
        # Check if user already had a purchase trial for this tier
        if hasattr(user, f'{trial_tier}_trial_used') and getattr(user, f'{trial_tier}_trial_used'):
            return f"User {user.email} already used their {trial_tier} trial"
        
        # Set 7-day trial before payment
        trial_start = datetime.now()
        trial_end = trial_start + timedelta(days=7)
        
        user.trial_start_date = trial_start
        user.trial_end_date = trial_end
        user.trial_tier = trial_tier
        user.is_trial_active = True
        user.subscription_tier = 'trial'
        
        # Set posting frequency
        if trial_tier == 'premium':
            user.post_frequency_hours = 3  # 8 posts per day
        elif trial_tier == 'pro':
            user.post_frequency_hours = 1  # 24 posts per day
        
        db.session.commit()
        
        return f"🎯 Started 7-day {trial_tier} trial for {user.email} - payment will be processed on {trial_end.strftime('%Y-%m-%d')}"
    
    def grant_contest_lifetime(self, user_email, tier='pro'):
        """Grant lifetime access to a contest winner"""
        user = User.query.filter_by(email=user_email).first()
        if not user:
            return f"User with email {user_email} not found"
        
        # Grant lifetime access
        user.subscription_tier = 'lifetime'
        user.contest_winner = True
        user.subscription_start_date = datetime.now()
        
        # Set unlimited posting frequency for lifetime
        user.post_frequency_hours = 1  # 24 posts per day
        user.auto_post_enabled = True
        
        db.session.commit()
        
        return f"🏆 Granted LIFETIME access to contest winner {user.email}! They now have unlimited features."
    
    def check_trial_status(self, user):
        """Check if user's trial has expired and update accordingly"""
        if user.is_trial_active and user.trial_end_date:
            if datetime.now() > user.trial_end_date:
                # Trial expired, revert to free tier
                user.is_trial_active = False
                user.subscription_tier = 'free'
                user.post_frequency_hours = 12  # Back to 2 posts per day
                user.trial_tier = None
                db.session.commit()
                return f"Trial expired for {user.email}, reverted to free tier"
        return None
    
    def get_user_access_level(self, user):
        """Get current access level for a user"""
        # Check trial expiration first
        self.check_trial_status(user)
        
        if user.subscription_tier == 'lifetime' or user.contest_winner:
            return {
                'tier': 'lifetime',
                'posts_per_day': 24,
                'features': ['All platforms', 'AI automation', 'Analytics', 'Affiliate program', 'Priority support'],
                'status': '🏆 Lifetime Access'
            }
        elif user.is_trial_active and user.trial_end_date > datetime.now():
            days_left = (user.trial_end_date - datetime.now()).days
            return {
                'tier': f'{user.trial_tier}_trial',
                'posts_per_day': 8 if user.trial_tier == 'premium' else 24,
                'features': ['All platforms', 'AI automation', 'Analytics'] + (['Affiliate program'] if user.trial_tier == 'pro' else []),
                'status': f'🎯 {user.trial_tier.title()} Trial ({days_left} days left)'
            }
        elif user.subscription_tier == 'premium':
            return {
                'tier': 'premium',
                'posts_per_day': 8,
                'features': ['All platforms', 'AI automation', 'Analytics', 'Priority support'],
                'status': '⭐ Premium Member'
            }
        elif user.subscription_tier == 'pro':
            return {
                'tier': 'pro', 
                'posts_per_day': 24,
                'features': ['All platforms', 'AI automation', 'Analytics', 'Affiliate program', 'White-label'],
                'status': '🚀 Pro Member'
            }
        else:
            return {
                'tier': 'free',
                'posts_per_day': 2,
                'features': ['Discord integration', 'Basic analytics', 'Email support'],
                'status': '🆓 Free Tier'
            }
    
    def list_trial_users(self):
        """List all users currently on trial"""
        trial_users = User.query.filter_by(is_trial_active=True).all()
        result = []
        for user in trial_users:
            days_left = (user.trial_end_date - datetime.now()).days if user.trial_end_date else 0
            result.append({
                'email': user.email,
                'trial_tier': user.trial_tier,
                'days_left': days_left,
                'expires': user.trial_end_date.strftime('%Y-%m-%d') if user.trial_end_date else 'Unknown'
            })
        return result
    
    def list_lifetime_users(self):
        """List all lifetime access users"""
        lifetime_users = User.query.filter(
            (User.subscription_tier == 'lifetime') | (User.contest_winner == True)
        ).all()
        result = []
        for user in lifetime_users:
            result.append({
                'email': user.email,
                'type': 'Contest Winner' if user.contest_winner else 'Lifetime',
                'granted': user.subscription_start_date.strftime('%Y-%m-%d') if user.subscription_start_date else 'Unknown'
            })
        return result

# Admin functions for easy management
def grant_premium_trial(email, days=30):
    """Quick function to grant premium trial"""
    manager = UserManager()
    return manager.grant_trial_access(email, 'premium', days)

def grant_pro_trial(email, days=30):
    """Quick function to grant pro trial"""
    manager = UserManager()
    return manager.grant_trial_access(email, 'pro', days)

def grant_contest_winner(email):
    """Quick function to grant contest winner lifetime access"""
    manager = UserManager()
    return manager.grant_contest_lifetime(email)