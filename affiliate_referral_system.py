"""
Affiliate Referral Commission System
Multi-tier commission structure with lifetime access rewards
"""
import os
import uuid
from datetime import datetime, timedelta
from app import app, db
from models import User

class AffiliateReferralSystem:
    """Manage affiliate referrals and commission tracking"""
    
    # Commission tiers based on total referral revenue
    COMMISSION_TIERS = {
        'bronze': {'min_revenue': 0, 'rate': 0.10, 'name': 'Bronze Affiliate'},
        'silver': {'min_revenue': 500, 'rate': 0.15, 'name': 'Silver Affiliate'},
        'gold': {'min_revenue': 1500, 'rate': 0.20, 'name': 'Gold Affiliate'},
        'platinum': {'min_revenue': 3000, 'rate': 0.25, 'name': 'Platinum Affiliate'},
        'diamond': {'min_revenue': 5000, 'rate': 0.30, 'name': 'Diamond Affiliate (Lifetime Access)'}
    }
    
    def __init__(self):
        pass
    
    def generate_affiliate_link(self, user_id):
        """Generate unique affiliate link for user"""
        with app.app_context():
            user = User.query.get(user_id)
            if not user:
                return None
                
            if not user.affiliate_code:
                # Generate unique affiliate code
                user.affiliate_code = f"ABP{uuid.uuid4().hex[:8].upper()}"
                user.affiliate_enabled = True
                db.session.commit()
            
            base_url = os.environ.get('REPLIT_DEV_DOMAIN', 'localhost:5000')
            return f"https://{base_url}/?ref={user.affiliate_code}"
    
    def track_referral_signup(self, affiliate_code, new_user_email):
        """Track when someone signs up via affiliate link"""
        with app.app_context():
            # Find referring user
            referrer = User.query.filter_by(affiliate_code=affiliate_code).first()
            if not referrer:
                return False
            
            # Find new user
            new_user = User.query.filter_by(email=new_user_email).first()
            if not new_user:
                return False
            
            # Set referral relationship
            new_user.referred_by = referrer.id
            referrer.total_referrals = (referrer.total_referrals or 0) + 1
            
            db.session.commit()
            return True
    
    def process_subscription_payment(self, user_id, amount, plan_type):
        """Process payment and calculate affiliate commission"""
        with app.app_context():
            user = User.query.get(user_id)
            if not user or not user.referred_by:
                return None
            
            # Get referrer
            referrer = User.query.get(user.referred_by)
            if not referrer:
                return None
            
            # Calculate commission
            current_tier = self.get_user_tier(referrer.id)
            commission_rate = self.COMMISSION_TIERS[current_tier]['rate']
            commission_amount = float(amount) * commission_rate
            
            # Update referrer's earnings
            referrer.total_referral_revenue = (referrer.total_referral_revenue or 0) + float(amount)
            referrer.total_commission_earned = (referrer.total_commission_earned or 0) + commission_amount
            referrer.pending_commission = (referrer.pending_commission or 0) + commission_amount
            
            # Check for lifetime access unlock
            if referrer.total_referral_revenue >= 5000 and not referrer.lifetime_access:
                referrer.lifetime_access = True
                referrer.subscription_tier = 'lifetime'
                self.notify_lifetime_access_unlocked(referrer)
            
            # Update user's subscription
            user.subscription_tier = plan_type
            user.subscription_start_date = datetime.now()
            
            db.session.commit()
            
            return {
                'referrer_id': referrer.id,
                'commission_amount': commission_amount,
                'new_tier': self.get_user_tier(referrer.id),
                'total_revenue': referrer.total_referral_revenue,
                'lifetime_unlocked': referrer.lifetime_access
            }
    
    def get_user_tier(self, user_id):
        """Get user's current affiliate tier"""
        with app.app_context():
            user = User.query.get(user_id)
            if not user:
                return 'bronze'
            
            revenue = user.total_referral_revenue or 0
            
            for tier, info in reversed(self.COMMISSION_TIERS.items()):
                if revenue >= info['min_revenue']:
                    return tier
            
            return 'bronze'
    
    def get_affiliate_dashboard_data(self, user_id):
        """Get comprehensive affiliate dashboard data"""
        with app.app_context():
            user = User.query.get(user_id)
            if not user:
                return None
            
            current_tier = self.get_user_tier(user_id)
            tier_info = self.COMMISSION_TIERS[current_tier]
            
            # Get next tier info
            next_tier = None
            for tier, info in self.COMMISSION_TIERS.items():
                if info['min_revenue'] > (user.total_referral_revenue or 0):
                    next_tier = {'name': tier, 'target': info['min_revenue']}
                    break
            
            # Get referral users
            referrals = User.query.filter_by(referred_by=user_id).all()
            
            return {
                'affiliate_code': user.affiliate_code,
                'affiliate_link': self.generate_affiliate_link(user_id),
                'current_tier': {
                    'name': current_tier,
                    'display_name': tier_info['name'],
                    'commission_rate': tier_info['rate'] * 100
                },
                'next_tier': next_tier,
                'stats': {
                    'total_referrals': user.total_referrals or 0,
                    'total_revenue': user.total_referral_revenue or 0,
                    'total_commission': user.total_commission_earned or 0,
                    'pending_commission': user.pending_commission or 0,
                    'lifetime_access': user.lifetime_access or False
                },
                'recent_referrals': [
                    {
                        'email': r.email,
                        'signup_date': r.created_at,
                        'subscription_tier': r.subscription_tier,
                        'status': 'Active' if r.subscription_tier != 'free' else 'Free'
                    }
                    for r in referrals[-10:]  # Last 10 referrals
                ],
                'progress_to_lifetime': {
                    'current': user.total_referral_revenue or 0,
                    'target': 5000,
                    'percentage': min(100, ((user.total_referral_revenue or 0) / 5000) * 100)
                }
            }
    
    def notify_lifetime_access_unlocked(self, user):
        """Notify user they've unlocked lifetime access"""
        # This would integrate with email system
        print(f"🎉 LIFETIME ACCESS UNLOCKED for {user.email}!")
        print(f"Total referral revenue: ${user.total_referral_revenue}")
    
    def get_admin_referral_analytics(self):
        """Get admin analytics for referral system"""
        with app.app_context():
            total_affiliates = User.query.filter(User.affiliate_enabled == True).count()
            total_referrals = User.query.filter(User.referred_by.isnot(None)).count()
            total_commission_paid = db.session.query(db.func.sum(User.total_commission_earned)).scalar() or 0
            total_referral_revenue = db.session.query(db.func.sum(User.total_referral_revenue)).scalar() or 0
            lifetime_users = User.query.filter(User.lifetime_access == True).count()
            
            # Tier distribution
            tier_stats = {}
            for tier in self.COMMISSION_TIERS.keys():
                count = 0
                users = User.query.filter(User.affiliate_enabled == True).all()
                for user in users:
                    if self.get_user_tier(user.id) == tier:
                        count += 1
                tier_stats[tier] = count
            
            return {
                'total_affiliates': total_affiliates,
                'total_referrals': total_referrals,
                'total_commission_paid': total_commission_paid,
                'total_referral_revenue': total_referral_revenue,
                'lifetime_users': lifetime_users,
                'tier_distribution': tier_stats,
                'conversion_rate': (total_referrals / max(total_affiliates, 1)) * 100
            }

def setup_admin_as_affiliate():
    """Set up admin user as affiliate for system promotion"""
    with app.app_context():
        admin = User.query.filter_by(email='drfe8694@gmail.com').first()
        if admin:
            affiliate_system = AffiliateReferralSystem()
            admin_link = affiliate_system.generate_affiliate_link(admin.id)
            print(f"🎯 Admin affiliate link: {admin_link}")
            print(f"🎯 Admin affiliate code: {admin.affiliate_code}")
            return admin_link
        return None

if __name__ == "__main__":
    setup_admin_as_affiliate()