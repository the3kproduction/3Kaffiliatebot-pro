#!/usr/bin/env python3
"""
Customer-facing server that works without authentication blocks
"""
import os
from flask import Flask, render_template, request, redirect, flash
import stripe

app = Flask(__name__)
app.secret_key = "customer-payments-work"

@app.route('/')
def home():
    return redirect('/subscribe')

@app.route('/subscribe')
def subscribe():
    """Working subscription page"""
    return render_template('subscribe.html', user=None, show_signup=True)

@app.route('/create-checkout-session', methods=['POST'])
def create_checkout_session():
    """Working Stripe checkout"""
    stripe.api_key = os.environ.get('STRIPE_SECRET_KEY')
    
    plan = request.form.get('plan')
    price_ids = {
        'premium': 'price_1RTCsLAjaTA9iq9Q4JF7UKrx',
        'pro': 'price_1RTCtOAjaTA9iq9QKNJJSUwF'
    }
    
    if plan not in price_ids:
        return redirect('/subscribe')
    
    try:
        domain = request.host_url.rstrip('/')
        checkout_session = stripe.checkout.Session.create(
            line_items=[{'price': price_ids[plan], 'quantity': 1}],
            mode='subscription',
            success_url=f'{domain}/success',
            cancel_url=f'{domain}/subscribe',
        )
        return redirect(checkout_session.url, code=303)
    except Exception as e:
        return f"Stripe error: {e}"

@app.route('/success')
def success():
    return "Payment successful! Your subscription is active."

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5002, debug=True)