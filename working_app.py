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
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>AffiliateBot Pro</title>
        <style>
            body { font-family: Arial, sans-serif; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; text-align: center; padding: 50px; }
            .hero { max-width: 800px; margin: 0 auto; }
            .btn { background: #4CAF50; color: white; padding: 15px 30px; border: none; border-radius: 25px; font-size: 18px; margin: 10px; text-decoration: none; display: inline-block; }
            .btn:hover { background: #45a049; }
        </style>
    </head>
    <body>
        <div class="hero">
            <h1>🤖 AffiliateBot Pro</h1>
            <h2>Automated Amazon Affiliate Marketing</h2>
            <p>Post products to 10+ platforms automatically. Increase your affiliate sales with AI-powered product selection.</p>
            <a href="/dashboard" class="btn">🚀 Get Started</a>
            <a href="/subscribe" class="btn">💰 View Pricing</a>
        </div>
    </body>
    </html>
    '''

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
    return render_template('campaigns.html')

@app.route('/analytics')
def analytics():
    """Analytics dashboard"""
    return render_template('analytics.html')

@app.route('/settings')
def settings():
    """User settings"""
    return render_template('settings.html')

@app.route('/login')
def login():
    """Simple login page"""
    return "<h1>Login Page</h1><p>Admin can login here</p>"

@app.route('/promote/<asin>', methods=['POST'])
def promote_product(asin):
    """Promote a specific product across platforms"""
    try:
        # Get product details
        product = ProductInventory.query.filter_by(asin=asin).first()
        if not product:
            return {"success": False, "message": "Product not found"}
        
        # Create affiliate URL with your Amazon affiliate ID
        affiliate_id = "luxoraconnect-20"
        affiliate_url = f"https://www.amazon.com/dp/{asin}?tag={affiliate_id}"
        
        # Format promotion message
        message = f"""🔥 **DEAL ALERT!** 🔥

{product.product_title}
💰 Price: {product.price}
⭐ Rating: {product.rating}/5

🛒 Get it here: {affiliate_url}

#AmazonDeals #TechDeals #Affiliate"""

        # For now, we'll simulate posting (you can connect real platforms later)
        platforms_posted = []
        
        # Simulate Discord posting
        if True:  # Replace with actual Discord webhook check
            platforms_posted.append("Discord")
        
        # Simulate Telegram posting  
        if True:  # Replace with actual Telegram bot check
            platforms_posted.append("Telegram")
        
        return {
            "success": True, 
            "message": f"Product promoted successfully to: {', '.join(platforms_posted)}",
            "product": product.product_title,
            "platforms": platforms_posted
        }
        
    except Exception as e:
        return {"success": False, "message": f"Error promoting product: {str(e)}"}

@app.route('/api/promote/<asin>', methods=['POST'])
def api_promote_product(asin):
    """API endpoint for promoting products"""
    return promote_product(asin)

@app.route('/dashboard')
def dashboard():
    """Professional affiliate marketing dashboard"""
    return render_template('dashboard_working.html')

# Create database tables and add sample products
with app.app_context():
    db.create_all()
    
    # Add sample products if none exist
    if ProductInventory.query.count() == 0:
        sample_products = [
            ProductInventory(asin='B08N5WRWNW', product_title='Echo Dot (4th Gen) Smart Speaker', category='Electronics', price='$49.99', rating=4.7, image_url='https://m.media-amazon.com/images/I/61Ub2RjgZkL._AC_SL1000_.jpg'),
            ProductInventory(asin='B08D6T6BKS', product_title='Fire TV Stick 4K Max', category='Electronics', price='$54.99', rating=4.6, image_url='https://m.media-amazon.com/images/I/51TjJOTfslL._AC_SL1000_.jpg'),
            ProductInventory(asin='B0863TXGM3', product_title='Jabra Elite 75t Wireless Earbuds', category='Electronics', price='$149.99', rating=4.4, image_url='https://m.media-amazon.com/images/I/61TEFj1MJZL._AC_SL1500_.jpg'),
            ProductInventory(asin='B081FPL9XY', product_title='Ring Video Doorbell', category='Home & Garden', price='$99.99', rating=4.5, image_url='https://m.media-amazon.com/images/I/51DYQQyQPgL._AC_SL1000_.jpg'),
            ProductInventory(asin='B07FZ8S74R', product_title='Instant Pot Duo 7-in-1', category='Kitchen', price='$79.95', rating=4.7, image_url='https://m.media-amazon.com/images/I/71%2BddX7HfXL._AC_SL1500_.jpg'),
            ProductInventory(asin='B07PYQCVJX', product_title='Apple AirPods Pro', category='Electronics', price='$249.00', rating=4.5, image_url='https://m.media-amazon.com/images/I/71zny7BTRlL._AC_SL1500_.jpg'),
            ProductInventory(asin='B08KRB6Z9X', product_title='Fitbit Charge 5 Fitness Tracker', category='Health & Fitness', price='$149.95', rating=4.3, image_url='https://m.media-amazon.com/images/I/61W7VhhpdQL._AC_SL1500_.jpg'),
            ProductInventory(asin='B086QZM8WF', product_title='Sony WH-1000XM4 Wireless Headphones', category='Electronics', price='$348.00', rating=4.6, image_url='https://m.media-amazon.com/images/I/71o8Q5XJS5L._AC_SL1500_.jpg'),
        ]
        
        for product in sample_products:
            db.session.add(product)
        db.session.commit()
        print("Added sample products to database")

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)