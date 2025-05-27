"""
Customer-facing app without authentication restrictions
"""
import os
from flask import Flask, render_template, request, redirect, flash
import stripe

# Create separate app for customer pages
customer_app = Flask(__name__)
customer_app.secret_key = os.environ.get("FLASK_SECRET_KEY") or "customer-secret"

@customer_app.route('/subscribe')
def subscribe():
    """Subscription page accessible to everyone"""
    return render_template('subscribe.html', user=None, show_signup=True)

@customer_app.route('/pricing')
def pricing():
    """Pricing page accessible to everyone"""
    return render_template('subscribe.html', user=None, show_signup=True)

@customer_app.route('/create-checkout-session', methods=['POST'])
def create_checkout_session():
    """Create Stripe checkout session"""
    stripe.api_key = os.environ.get('STRIPE_SECRET_KEY')
    
    plan = request.form.get('plan')
    
    # Stripe Price IDs
    price_ids = {
        'premium': 'price_1RTCsLAjaTA9iq9Q4JF7UKrx',  # $29/month
        'pro': 'price_1RTCtOAjaTA9iq9QKNJJSUwF'        # $79/month
    }
    
    if plan not in price_ids:
        flash('Invalid plan selected', 'error')
        return redirect('/subscribe')
    
    try:
        domain = request.host_url.rstrip('/')
        
        checkout_session = stripe.checkout.Session.create(
            line_items=[{
                'price': price_ids[plan],
                'quantity': 1,
            }],
            mode='subscription',
            success_url=f'{domain}/success?session_id={{CHECKOUT_SESSION_ID}}',
            cancel_url=f'{domain}/subscribe',
            metadata={'plan': plan}
        )
        
        return redirect(checkout_session.url, code=303)
        
    except Exception as e:
        flash(f'Error: {str(e)}', 'error')
        return redirect('/subscribe')

if __name__ == '__main__':
    customer_app.run(host="0.0.0.0", port=5001, debug=True)