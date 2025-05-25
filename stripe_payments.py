"""
Stripe Payment Processing for AffiliateBot Pro
Handles subscription payments and affiliate commission tracking
"""
import os
import stripe
from flask import request, jsonify, redirect, url_for
from app import app, db
from models import User
from affiliate_referral_system import AffiliateReferralSystem
import logging

logger = logging.getLogger(__name__)

# Initialize Stripe
stripe.api_key = os.environ.get('STRIPE_SECRET_KEY')

class StripePaymentProcessor:
    """Handle Stripe payments and subscription management"""
    
    def __init__(self):
        self.domain = self.get_domain()
        self.affiliate_system = AffiliateReferralSystem()
    
    def get_domain(self):
        """Get the current domain for Stripe redirects"""
        if os.environ.get('REPLIT_DEPLOYMENT'):
            return os.environ.get('REPLIT_DEV_DOMAIN', 'localhost:5000')
        else:
            domains = os.environ.get('REPLIT_DOMAINS', 'localhost:5000')
            return domains.split(',')[0]
    
    def create_checkout_session(self, user_id, plan_type, affiliate_code=None):
        """Create Stripe checkout session for subscription"""
        try:
            user = User.query.get(user_id)
            if not user:
                return {'error': 'User not found'}
            
            # Define subscription plans
            plans = {
                'premium': {
                    'price': 2900,  # $29.00 in cents
                    'name': 'AffiliateBot Pro Premium',
                    'description': '8 posts per day, priority support'
                },
                'pro': {
                    'price': 7900,  # $79.00 in cents
                    'name': 'AffiliateBot Pro Professional',
                    'description': '24 posts per day, unlimited platforms, priority support'
                }
            }
            
            if plan_type not in plans:
                return {'error': 'Invalid plan type'}
            
            plan = plans[plan_type]
            
            # Create checkout session
            checkout_session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=[{
                    'price_data': {
                        'currency': 'usd',
                        'recurring': {
                            'interval': 'month'
                        },
                        'product_data': {
                            'name': plan['name'],
                            'description': plan['description'],
                        },
                        'unit_amount': plan['price'],
                    },
                    'quantity': 1,
                }],
                mode='subscription',
                success_url=f'https://{self.domain}/payment-success?session_id={{CHECKOUT_SESSION_ID}}',
                cancel_url=f'https://{self.domain}/payment-cancelled',
                client_reference_id=user_id,
                metadata={
                    'user_id': user_id,
                    'plan_type': plan_type,
                    'affiliate_code': affiliate_code or '',
                    'user_email': user.email
                }
            )
            
            return {'checkout_url': checkout_session.url, 'session_id': checkout_session.id}
            
        except Exception as e:
            logger.error(f"Stripe checkout error: {e}")
            return {'error': str(e)}
    
    def handle_successful_payment(self, session_id):
        """Handle successful payment and upgrade user"""
        try:
            # Retrieve the checkout session
            session = stripe.checkout.Session.retrieve(session_id)
            
            if session.payment_status != 'paid':
                return {'error': 'Payment not completed'}
            
            user_id = session.metadata.get('user_id')
            plan_type = session.metadata.get('plan_type')
            affiliate_code = session.metadata.get('affiliate_code')
            
            # Get user
            user = User.query.get(user_id)
            if not user:
                return {'error': 'User not found'}
            
            # Calculate amount paid
            amount_paid = session.amount_total / 100  # Convert from cents
            
            # Process affiliate commission if there's a referrer
            commission_info = None
            if affiliate_code:
                # Track referral signup first
                self.affiliate_system.track_referral_signup(affiliate_code, user.email)
                
                # Process commission
                commission_info = self.affiliate_system.process_subscription_payment(
                    user_id, amount_paid, plan_type
                )
            
            # Upgrade user subscription
            user.subscription_tier = plan_type
            user.subscription_start_date = db.func.now()
            
            # Set post limits based on plan
            if plan_type == 'premium':
                user.post_frequency_hours = 3  # 8 posts per day
            elif plan_type == 'pro':
                user.post_frequency_hours = 1  # 24 posts per day
            
            db.session.commit()
            
            return {
                'success': True,
                'user_id': user_id,
                'plan_type': plan_type,
                'amount_paid': amount_paid,
                'commission_info': commission_info
            }
            
        except Exception as e:
            logger.error(f"Payment processing error: {e}")
            return {'error': str(e)}
    
    def create_customer_portal_session(self, user_id):
        """Create customer portal session for subscription management"""
        try:
            user = User.query.get(user_id)
            if not user:
                return {'error': 'User not found'}
            
            # Create portal session
            portal_session = stripe.billing_portal.Session.create(
                return_url=f'https://{self.domain}/dashboard',
                # You would need to store the customer ID when creating subscriptions
            )
            
            return {'portal_url': portal_session.url}
            
        except Exception as e:
            logger.error(f"Customer portal error: {e}")
            return {'error': str(e)}

def test_stripe_connection():
    """Test Stripe API connection"""
    try:
        # Test API key by listing payment methods
        payment_methods = stripe.PaymentMethod.list(limit=1)
        print("✅ Stripe connection successful!")
        return True
    except stripe.error.AuthenticationError:
        print("❌ Stripe API key invalid")
        return False
    except Exception as e:
        print(f"❌ Stripe connection error: {e}")
        return False

if __name__ == "__main__":
    test_stripe_connection()