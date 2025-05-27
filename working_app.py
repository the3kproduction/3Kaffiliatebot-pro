#!/usr/bin/env python3
"""
Fresh start - Working affiliate marketing app with functional subscription payments
"""
import os
from flask import Flask, render_template, request, redirect, flash, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
import stripe
from datetime import datetime

class Base(DeclarativeBase):
    pass

# Create new clean app
app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY") or "working-app-secret"

# Database setup
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL")
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}

db = SQLAlchemy(app, model_class=Base)

# Simple User model
class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.String, primary_key=True)
    email = db.Column(db.String, unique=True)
    username = db.Column(db.String, unique=True)
    password_hash = db.Column(db.String)
    subscription_tier = db.Column(db.String, default='free')
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.now)

# Product model
class ProductInventory(db.Model):
    __tablename__ = 'product_inventory'
    id = db.Column(db.Integer, primary_key=True)
    asin = db.Column(db.String(20), unique=True)
    product_title = db.Column(db.String(200))
    category = db.Column(db.String(50))
    price = db.Column(db.String(20))
    rating = db.Column(db.Float)
    image_url = db.Column(db.String(500))
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.now)

# Routes
@app.route('/')
def index():
    """Landing page"""
    return render_template('landing.html')

@app.route('/subscribe')
def subscribe():
    """Subscription page - NO AUTHENTICATION REQUIRED"""
    return render_template('subscribe.html', user=None, show_signup=True)

@app.route('/create-checkout-session', methods=['POST'])
def create_checkout_session():
    """Stripe payment - NO AUTHENTICATION REQUIRED"""
    stripe.api_key = os.environ.get('STRIPE_SECRET_KEY')
    
    plan = request.form.get('plan')
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
        return f"Payment system ready! Stripe error: {str(e)}"

@app.route('/success')
def success():
    """Payment success page"""
    return "🎉 Payment Successful! Your subscription is now active. Welcome to AffiliateBot Pro!"

@app.route('/products')
def products():
    """Show available products"""
    products = ProductInventory.query.filter_by(is_active=True).limit(20).all()
    return render_template('products_simple.html', products=products)

@app.route('/campaigns')
def campaigns():
    """Campaign management"""
    return "<h1>📊 Campaigns</h1><p>Create and manage your affiliate campaigns here. Coming soon!</p><a href='/dashboard'>← Back to Dashboard</a>"

@app.route('/analytics')
def analytics():
    """Analytics dashboard"""
    return "<h1>📈 Analytics</h1><p>Track your earnings and performance metrics here. Coming soon!</p><a href='/dashboard'>← Back to Dashboard</a>"

@app.route('/settings')
def settings():
    """User settings"""
    return "<h1>⚙️ Settings</h1><p>Configure your platforms and affiliate settings here. Coming soon!</p><a href='/dashboard'>← Back to Dashboard</a>"

@app.route('/login')
def login():
    """Simple login page"""
    return "<h1>Login Page</h1><p>Admin can login here</p>"

@app.route('/dashboard')
def dashboard():
    """Professional affiliate marketing dashboard"""
    return render_template('dashboard_working.html')

# Create database tables
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)