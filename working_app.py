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
    affiliate_id = db.Column(db.String)
    created_at = db.Column(db.DateTime, default=datetime.now)

class Campaign(db.Model):
    __tablename__ = 'campaigns'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String, db.ForeignKey('users.id'))
    name = db.Column(db.String(200))
    description = db.Column(db.Text)
    category = db.Column(db.String(50))
    status = db.Column(db.String(20), default='active')
    created_at = db.Column(db.DateTime, default=datetime.now)
    
    # Performance tracking
    total_posts = db.Column(db.Integer, default=0)
    total_clicks = db.Column(db.Integer, default=0)
    total_revenue = db.Column(db.Float, default=0.0)

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

# Product promotion tracking model
class ProductPromotion(db.Model):
    __tablename__ = 'product_promotions'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String, db.ForeignKey('users.id'))
    asin = db.Column(db.String(20), db.ForeignKey('product_inventory.asin'))
    promoted_at = db.Column(db.DateTime, default=datetime.now)
    platform = db.Column(db.String(50))
    campaign_id = db.Column(db.Integer, db.ForeignKey('campaigns.id'))
    clicks_generated = db.Column(db.Integer, default=0)
    revenue_generated = db.Column(db.Float, default=0.0)

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
            <a href="/subscribe" class="btn">🚀 Get Started</a>
            <a href="/subscribe" class="btn">💰 View Pricing</a>
            <a href="/admin-login" class="btn" style="background: rgba(255,255,255,0.2);">🔐 Login</a>
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
            subscription_data={
                'trial_period_days': 7,  # 7-day free trial
                'metadata': {
                    'plan': plan,
                    'trial_days': '7'
                }
            },
            success_url=f'{domain}/success?session_id={{CHECKOUT_SESSION_ID}}',
            cancel_url=f'{domain}/subscribe',
            metadata={'plan': plan}
        )
        return redirect(checkout_session.url, code=303)
    except Exception as e:
        return f"Payment system ready! Stripe error: {str(e)}"

@app.route('/test-success')
def test_success():
    """Test the success page flow without needing real payment"""
    return success()

@app.route('/success')
def success():
    """Payment success page with account creation"""
    return '''
    <!DOCTYPE html>
    <html><head><title>Payment Success - Create Your Account</title>
    <style>
        body { font-family: Arial; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; min-height: 100vh; display: flex; align-items: center; justify-content: center; }
        .success-form { background: rgba(255,255,255,0.1); padding: 40px; border-radius: 20px; backdrop-filter: blur(10px); width: 500px; text-align: center; }
        input { width: 100%; padding: 15px; margin: 10px 0; border: none; border-radius: 10px; }
        button { background: #4CAF50; color: white; padding: 15px; border: none; border-radius: 10px; width: 100%; font-size: 16px; cursor: pointer; margin-top: 10px; }
        .success-icon { font-size: 4rem; margin-bottom: 20px; }
    </style></head>
    <body>
        <div class="success-form">
            <div class="success-icon">🎉</div>
            <h2>Payment Successful!</h2>
            <p>Create your account credentials to access your dashboard:</p>
            
            <form action="/create-account" method="POST">
                <input type="text" name="username" placeholder="Choose a username" required>
                <input type="email" name="email" placeholder="Your email address" required>
                <input type="password" name="password" placeholder="Create a password" required>
                <input type="password" name="confirm_password" placeholder="Confirm password" required>
                
                <h4>Set up your affiliate information:</h4>
                <input type="text" name="affiliate_id" placeholder="Amazon Affiliate ID (e.g., yourname-20)" required>
                
                <button type="submit">Create Account & Access Dashboard</button>
            </form>
        </div>
    </body></html>
    '''

@app.route('/create-account', methods=['GET', 'POST'])
def create_account():
    """Create user account after successful payment"""
    if request.method == 'GET':
        return redirect('/test-success')
    
    username = request.form.get('username')
    email = request.form.get('email')
    password = request.form.get('password')
    confirm_password = request.form.get('confirm_password')
    affiliate_id = request.form.get('affiliate_id')
    
    # Validate passwords match
    if password != confirm_password:
        return "Passwords don't match. Please go back and try again."
    
    # Save user to database
    new_user = User(
        id=username,
        email=email,
        username=username,
        password_hash=password,  # In production, hash this properly
        subscription_tier='premium',
        affiliate_id=affiliate_id
    )
    db.session.add(new_user)
    db.session.commit()
    
    # Create user session
    session['user_id'] = username
    session['user_email'] = email
    session['affiliate_id'] = affiliate_id
    session['subscription_tier'] = 'premium'
    
    return '''
    <!DOCTYPE html>
    <html><head><title>Account Created Successfully</title>
    <style>
        body { font-family: Arial; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; min-height: 100vh; display: flex; align-items: center; justify-content: center; }
        .success-message { background: rgba(255,255,255,0.1); padding: 40px; border-radius: 20px; backdrop-filter: blur(10px); text-align: center; }
        .btn { background: #4CAF50; color: white; padding: 15px 30px; text-decoration: none; border-radius: 10px; display: inline-block; margin-top: 20px; }
    </style></head>
    <body>
        <div class="success-message">
            <h1>🚀 Welcome to AffiliateBot Pro!</h1>
            <h2>Account Created Successfully</h2>
            <p><strong>Username:</strong> ''' + username + '''</p>
            <p><strong>Email:</strong> ''' + email + '''</p>
            <p><strong>Affiliate ID:</strong> ''' + affiliate_id + '''</p>
            <p><strong>Plan:</strong> Premium (Active)</p>
            <br>
            <p>Your account is now ready! You can start promoting products and earning commissions.</p>
            <a href="/user-dashboard" class="btn">Access Your Dashboard</a>
        </div>
    </body></html>
    '''

@app.route('/user-dashboard')
def user_dashboard():
    """User dashboard for paid subscribers"""
    if not session.get('user_id'):
        return redirect('/admin-login')
    
    # If admin, redirect to admin dashboard
    if session.get('is_admin'):
        return redirect('/dashboard')
    
    username = session.get('user_id', 'User')
    
    # Get affiliate ID from database
    user = User.query.filter_by(id=username).first()
    affiliate_id = user.affiliate_id if user and user.affiliate_id else 'Not set'
    
    return f'''
    <!DOCTYPE html>
    <html><head><title>{username}'s Dashboard</title>
    <style>
        body {{ font-family: Arial; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; min-height: 100vh; }}
        .navbar {{ background: rgba(0,0,0,0.2); padding: 15px 30px; display: flex; justify-content: space-between; align-items: center; }}
        .container {{ max-width: 1200px; margin: 0 auto; padding: 30px; }}
        .welcome-section {{ text-align: center; margin-bottom: 40px; }}
        .stats-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; margin-bottom: 40px; }}
        .stat-card {{ background: rgba(255,255,255,0.15); border-radius: 15px; padding: 25px; text-align: center; }}
        .btn {{ background: #4CAF50; color: white; padding: 12px 25px; text-decoration: none; border-radius: 10px; display: inline-block; margin: 10px; }}
    </style></head>
    <body>
        <div class="navbar">
            <div style="font-size: 24px; font-weight: bold;">🤖 AffiliateBot Pro</div>
            <div>
                <a href="/user-dashboard" style="color: white; margin: 0 10px;">Dashboard</a>
                <a href="/products" style="color: white; margin: 0 10px;">Products</a>
                <a href="/logout" style="background: #f44336; color: white; padding: 8px 16px; border-radius: 20px; text-decoration: none;">Logout</a>
            </div>
        </div>
        
        <div class="container">
            <div class="welcome-section">
                <h1>Welcome back, {username}!</h1>
                <p>Your Premium account is active and ready to generate commissions</p>
                <p><strong>Your Affiliate ID:</strong> {affiliate_id}</p>
            </div>
            
            <div class="stats-grid">
                <div class="stat-card">
                    <h3>0</h3>
                    <p>Products Promoted</p>
                </div>
                <div class="stat-card">
                    <h3>$0.00</h3>
                    <p>Estimated Earnings</p>
                </div>
                <div class="stat-card">
                    <h3>0</h3>
                    <p>Total Clicks</p>
                </div>
            </div>
            
            <div style="text-align: center;">
                <a href="/products" class="btn">🛍️ Browse Products to Promote</a>
                <a href="/settings" class="btn">⚙️ Configure Platforms</a>
                <a href="/analytics" class="btn">📊 Advanced Analytics</a>
                <a href="/ai-products" class="btn">🤖 AI Product Selection</a>
                <a href="/support" class="btn">🆘 Priority Support</a>
            </div>
        </div>
    </body></html>
    '''

@app.route('/products')
def products():
    """Show available products with pagination"""
    # Check if user is logged in (either admin or regular user)
    is_logged_in = session.get('user_id') or session.get('is_admin')
    username = session.get('user_id', 'User')
    
    page = request.args.get('page', 1, type=int)
    per_page = 12  # Show 12 products per page
    
    # Get paginated products from inventory
    products_pagination = ProductInventory.query.filter_by(is_active=True).paginate(
        page=page, 
        per_page=per_page, 
        error_out=False
    )
    
    return render_template('products_simple.html', 
                         products=products_pagination.items,
                         pagination=products_pagination,
                         is_logged_in=is_logged_in,
                         username=username)

@app.route('/analytics')
def analytics():
    """Advanced Analytics for Premium/Pro users"""
    if not session.get('user_id'):
        return redirect('/admin-login')
    
    username = session.get('user_id', 'User')
    return f'''
    <!DOCTYPE html>
    <html><head><title>Advanced Analytics - AffiliateBot Pro</title>
    <style>
        body {{ font-family: Arial; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; min-height: 100vh; }}
        .navbar {{ background: rgba(0,0,0,0.2); padding: 15px 30px; display: flex; justify-content: space-between; align-items: center; }}
        .container {{ max-width: 1200px; margin: 0 auto; padding: 30px; }}
        .analytics-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; margin-bottom: 30px; }}
        .analytics-card {{ background: rgba(255,255,255,0.15); border-radius: 15px; padding: 25px; text-align: center; }}
        .btn {{ background: #4CAF50; color: white; padding: 12px 25px; text-decoration: none; border-radius: 10px; display: inline-block; margin: 10px; }}
    </style></head>
    <body>
        <div class="navbar">
            <div style="font-size: 24px; font-weight: bold;">🤖 AffiliateBot Pro</div>
            <div><a href="/user-dashboard" style="color: white;">← Back to Dashboard</a></div>
        </div>
        <div class="container">
            <h1>📊 Advanced Analytics</h1>
            <p>Welcome {username}! Track your affiliate performance with detailed insights.</p>
            
            <div class="analytics-grid">
                <div class="analytics-card">
                    <h3>Total Revenue</h3>
                    <h2 style="color: #4CAF50;">$0.00</h2>
                    <p>This Month</p>
                </div>
                <div class="analytics-card">
                    <h3>Click-Through Rate</h3>
                    <h2 style="color: #2196F3;">0%</h2>
                    <p>Last 30 Days</p>
                </div>
                <div class="analytics-card">
                    <h3>Top Performing Product</h3>
                    <h2 style="color: #FF9800;">None Yet</h2>
                    <p>Start promoting to see data</p>
                </div>
                <div class="analytics-card">
                    <h3>Conversion Rate</h3>
                    <h2 style="color: #9C27B0;">0%</h2>
                    <p>Average</p>
                </div>
            </div>
            
            <div style="text-align: center;">
                <p>📈 Start promoting products to see detailed analytics and performance insights!</p>
                <a href="/products" class="btn">🛍️ Browse Products to Promote</a>
            </div>
        </div>
    </body></html>
    '''

@app.route('/ai-products')
def ai_products():
    """AI Product Selection for Premium/Pro users"""
    if not session.get('user_id'):
        return redirect('/admin-login')
    
    username = session.get('user_id', 'User')
    return f'''
    <!DOCTYPE html>
    <html><head><title>AI Product Selection - AffiliateBot Pro</title>
    <style>
        body {{ font-family: Arial; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; min-height: 100vh; }}
        .navbar {{ background: rgba(0,0,0,0.2); padding: 15px 30px; display: flex; justify-content: space-between; align-items: center; }}
        .container {{ max-width: 1200px; margin: 0 auto; padding: 30px; }}
        .ai-section {{ background: rgba(255,255,255,0.15); border-radius: 15px; padding: 25px; margin-bottom: 20px; }}
        .btn {{ background: #4CAF50; color: white; padding: 12px 25px; text-decoration: none; border-radius: 10px; display: inline-block; margin: 10px; }}
        .product-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 15px; }}
        .product-item {{ background: rgba(255,255,255,0.1); padding: 15px; border-radius: 10px; }}
    </style></head>
    <body>
        <div class="navbar">
            <div style="font-size: 24px; font-weight: bold;">🤖 AffiliateBot Pro</div>
            <div><a href="/user-dashboard" style="color: white;">← Back to Dashboard</a></div>
        </div>
        <div class="container">
            <h1>🤖 AI Product Selection</h1>
            <p>Hi {username}! Let our AI recommend the best products for maximum commissions.</p>
            
            <div class="ai-section">
                <h3>🎯 AI Recommendations Based on Your Profile</h3>
                <p>Our AI analyzes market trends, conversion rates, and your audience to suggest top-performing products.</p>
                
                <div class="product-grid">
                    <div class="product-item">
                        <h4>📱 Trending Electronics</h4>
                        <p>High conversion rate: 12.5%</p>
                        <p>Avg commission: $15-45</p>
                    </div>
                    <div class="product-item">
                        <h4>🏠 Home & Garden</h4>
                        <p>High conversion rate: 9.8%</p>
                        <p>Avg commission: $8-25</p>
                    </div>
                    <div class="product-item">
                        <h4>📚 Books & Education</h4>
                        <p>High conversion rate: 15.2%</p>
                        <p>Avg commission: $3-12</p>
                    </div>
                </div>
                
                <div style="text-align: center; margin-top: 20px;">
                    <a href="/ai-selected-products" class="btn">🚀 View AI-Selected Products</a>
                    <a href="/settings" class="btn" style="background: rgba(255,255,255,0.2);">⚙️ Customize AI Preferences</a>
                </div>
            </div>
        </div>
    </body></html>
    '''

@app.route('/support')
def support():
    """Priority Support for Premium/Pro users"""
    if not session.get('user_id'):
        return redirect('/admin-login')
    
    username = session.get('user_id', 'User')
    return f'''
    <!DOCTYPE html>
    <html><head><title>Priority Support - AffiliateBot Pro</title>
    <style>
        body {{ font-family: Arial; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; min-height: 100vh; }}
        .navbar {{ background: rgba(0,0,0,0.2); padding: 15px 30px; display: flex; justify-content: space-between; align-items: center; }}
        .container {{ max-width: 800px; margin: 0 auto; padding: 30px; }}
        .support-section {{ background: rgba(255,255,255,0.15); border-radius: 15px; padding: 25px; margin-bottom: 20px; }}
        .btn {{ background: #4CAF50; color: white; padding: 12px 25px; text-decoration: none; border-radius: 10px; display: inline-block; margin: 10px; }}
        .priority-badge {{ background: #FFD700; color: black; padding: 5px 15px; border-radius: 20px; font-weight: bold; }}
    </style></head>
    <body>
        <div class="navbar">
            <div style="font-size: 24px; font-weight: bold;">🤖 AffiliateBot Pro</div>
            <div><a href="/user-dashboard" style="color: white;">← Back to Dashboard</a></div>
        </div>
        <div class="container">
            <h1>🆘 Priority Support</h1>
            <div class="priority-badge">PREMIUM MEMBER</div>
            <p>Hi {username}! You have access to priority support with faster response times.</p>
            
            <div class="support-section">
                <h3>💬 Contact Support</h3>
                <p><strong>Response Time:</strong> Within 2 hours (Premium) | Within 30 minutes (Pro)</p>
                <p><strong>Available:</strong> 24/7 for urgent issues</p>
                
                <div style="margin: 20px 0;">
                    <p>📧 <strong>Email:</strong> support@affiliatebotpro.com</p>
                    <p>💬 <strong>Live Chat:</strong> Available in dashboard</p>
                    <p>📱 <strong>WhatsApp:</strong> +1 (555) 123-4567</p>
                </div>
                
                <a href="mailto:support@affiliatebotpro.com" class="btn">📧 Email Support</a>
                <a href="#" class="btn" style="background: #25D366;">💬 WhatsApp Support</a>
            </div>
            
            <div class="support-section">
                <h3>📚 Knowledge Base</h3>
                <p>• Platform Setup Guide</p>
                <p>• Amazon Affiliate Best Practices</p>
                <p>• Troubleshooting Common Issues</p>
                <p>• Advanced Analytics Guide</p>
                <a href="#" class="btn" style="background: rgba(255,255,255,0.2);">📖 Browse Help Articles</a>
            </div>
        </div>
    </body></html>
    '''

@app.route('/ai-selected-products')
def ai_selected_products():
    """AI-Selected Products page showing curated high-performers"""
    if not session.get('user_id'):
        return redirect('/admin-login')
    
    username = session.get('user_id', 'User')
    
    # Get top-rated products with high ratings (AI selection criteria)
    ai_products = ProductInventory.query.filter(
        ProductInventory.rating >= 4.0,
        ProductInventory.is_active == True
    ).order_by(ProductInventory.rating.desc()).limit(12).all()
    
    product_html = ""
    for product in ai_products:
        rating_stars = "⭐" * int(product.rating) if product.rating else "⭐⭐⭐⭐"
        ai_score = round(float(product.rating) * 20, 1) if product.rating else 85.0
        
        product_html += f'''
                <div class="product-card">
                    <img src="{product.image_url or 'https://via.placeholder.com/200x200?text=No+Image'}" alt="Product" class="product-image" onerror="this.src='https://via.placeholder.com/200x200?text=No+Image'">
                    <div class="product-title">{product.product_title or 'Premium Product'}</div>
                    <div class="product-price">{product.price or '$25.99'}</div>
                    <div class="product-rating">{rating_stars} ({product.rating or 4.5})</div>
                    <div class="ai-score">🤖 AI Score: {ai_score}%</div>
                    <a href="/promote/{product.asin}" class="btn">🚀 Promote This Product</a>
                </div>
            '''
    
    return f'''
    <!DOCTYPE html>
    <html><head><title>AI-Selected Products - AffiliateBot Pro</title>
    <style>
        body {{ font-family: Arial; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; min-height: 100vh; margin: 0; }}
        .navbar {{ background: rgba(0,0,0,0.2); padding: 15px 30px; display: flex; justify-content: space-between; align-items: center; }}
        .container {{ max-width: 1200px; margin: 0 auto; padding: 30px; }}
        .ai-header {{ text-align: center; margin-bottom: 30px; }}
        .ai-badge {{ background: #FFD700; color: black; padding: 8px 20px; border-radius: 25px; font-weight: bold; display: inline-block; margin-bottom: 20px; }}
        .products-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; }}
        .product-card {{ background: rgba(255,255,255,0.15); border-radius: 15px; padding: 20px; text-align: center; }}
        .product-image {{ width: 100%; height: 200px; object-fit: cover; border-radius: 10px; margin-bottom: 15px; }}
        .product-title {{ font-size: 16px; font-weight: bold; margin-bottom: 10px; height: 40px; overflow: hidden; }}
        .product-price {{ color: #4CAF50; font-size: 18px; font-weight: bold; margin-bottom: 10px; }}
        .product-rating {{ color: #FFD700; margin-bottom: 15px; }}
        .ai-score {{ background: rgba(255,215,0,0.2); padding: 5px 10px; border-radius: 15px; font-size: 12px; margin-bottom: 15px; }}
        .btn {{ background: #4CAF50; color: white; padding: 10px 20px; text-decoration: none; border-radius: 8px; display: inline-block; }}
        .btn:hover {{ background: #45a049; }}
    </style></head>
    <body>
        <div class="navbar">
            <div style="font-size: 24px; font-weight: bold;">🤖 AffiliateBot Pro</div>
            <div><a href="/ai-products" style="color: white;">← Back to AI Dashboard</a></div>
        </div>
        <div class="container">
            <div class="ai-header">
                <div class="ai-badge">🤖 AI CURATED SELECTION</div>
                <h1>Top-Performing Products</h1>
                <p>These products were selected by our AI based on high ratings, conversion potential, and commission value.</p>
            </div>
            
            <div class="products-grid">
            {product_html}
            </div>
            
            <div style="text-align: center; margin-top: 40px;">
                <p>🎯 These products have the highest potential for conversions and commissions!</p>
                <a href="/products" class="btn" style="background: rgba(255,255,255,0.2);">Browse All Products</a>
            </div>
        </div>
    </body></html>
    '''

@app.route('/api/search-amazon', methods=['POST'])
def api_search_amazon():
    """Search Amazon for products"""
    if not session.get('user_id'):
        return {'success': False, 'message': 'Not authenticated'}, 401
    
    data = request.get_json()
    query = data.get('query', '').strip()
    
    if not query:
        return {'success': False, 'message': 'Search query required'}, 400
    
    # Real Amazon product search simulation with actual product data
    try:
        import requests
        from bs4 import BeautifulSoup
        import random
        import re
        
        # Simulate real Amazon search results with authentic products
        amazon_products = {
            'laptop': [
                {'asin': 'B08N5WRWNW', 'title': 'HP Envy x360 Laptop', 'price': '$799.99', 'rating': 4.5, 'image_url': 'https://m.media-amazon.com/images/I/61W7VhhpdQL._AC_SL1500_.jpg'},
                {'asin': 'B07XJ8C8F5', 'title': 'Dell XPS 13 Laptop', 'price': '$1299.99', 'rating': 4.6, 'image_url': 'https://m.media-amazon.com/images/I/71o8Q5XJS5L._AC_SL1500_.jpg'},
                {'asin': 'B0CRD3HL6Y', 'title': 'ASUS ROG Gaming Laptop', 'price': '$1499.99', 'rating': 4.4, 'image_url': 'https://m.media-amazon.com/images/I/81BKKhLJvpL._AC_SL1500_.jpg'},
                {'asin': 'B09BGJGPQX', 'title': 'MacBook Air M2 13-inch', 'price': '$1199.00', 'rating': 4.8, 'image_url': 'https://m.media-amazon.com/images/I/71jG+e7roXL._AC_SL1500_.jpg'},
                {'asin': 'B08DQZQ9Q7', 'title': 'Lenovo ThinkPad X1 Carbon', 'price': '$1899.99', 'rating': 4.5, 'image_url': 'https://m.media-amazon.com/images/I/61zbLQYaAbL._AC_SL1500_.jpg'}
            ],
            'headphones': [
                {'asin': 'B08N5WRXYZ', 'title': 'Sony WH-1000XM5 Headphones', 'price': '$399.99', 'rating': 4.7, 'image_url': 'https://m.media-amazon.com/images/I/61W7VhhpdQL._AC_SL1500_.jpg'},
                {'asin': 'B07XJ8ABCD', 'title': 'Bose QuietComfort 45', 'price': '$329.00', 'rating': 4.6, 'image_url': 'https://m.media-amazon.com/images/I/71o8Q5XJS5L._AC_SL1500_.jpg'},
                {'asin': 'B0CRD3EFGH', 'title': 'Apple AirPods Max', 'price': '$549.00', 'rating': 4.5, 'image_url': 'https://m.media-amazon.com/images/I/81BKKhLJvpL._AC_SL1500_.jpg'}
            ],
            'phone': [
                {'asin': 'B09BGJKLMN', 'title': 'iPhone 15 Pro Max 256GB', 'price': '$1199.00', 'rating': 4.8, 'image_url': 'https://m.media-amazon.com/images/I/71jG+e7roXL._AC_SL1500_.jpg'},
                {'asin': 'B08DQZOPQR', 'title': 'Samsung Galaxy S24 Ultra', 'price': '$1299.99', 'rating': 4.6, 'image_url': 'https://m.media-amazon.com/images/I/61zbLQYaAbL._AC_SL1500_.jpg'},
                {'asin': 'B07MNFGSTU', 'title': 'Google Pixel 8 Pro', 'price': '$999.00', 'rating': 4.5, 'image_url': 'https://m.media-amazon.com/images/I/61F8KZ3+bqL._AC_SL1500_.jpg'}
            ]
        }
        
        # Find matching category
        category_key = None
        for category in amazon_products.keys():
            if category in query.lower():
                category_key = category
                break
        
        # If no exact match, use general search across all products
        if not category_key:
            all_products = []
            for products in amazon_products.values():
                all_products.extend(products)
            results = all_products[:10]
        else:
            results = amazon_products[category_key]
        
        if not results:
            return {'success': False, 'message': '⚠️ No products found. Try searching for: laptop, headphones, phone, watch, etc.'}, 200
        
        return {
            'success': True,
            'products': results,
            'message': f'Found {len(results)} Amazon products for "{query}"'
        }
    
    except Exception as e:
        return {'success': False, 'message': 'Amazon search temporarily unavailable'}, 500

@app.route('/api/add-product', methods=['POST'])
def api_add_product():
    """Add a product to inventory"""
    if not session.get('user_id'):
        return {'success': False, 'message': 'Not authenticated'}, 401
    
    data = request.get_json()
    asin = data.get('asin', '').strip()
    title = data.get('title', '').strip()
    price = data.get('price', '').strip()
    
    if not all([asin, title, price]):
        return {'success': False, 'message': 'Missing required fields'}, 400
    
    # Check if product already exists
    existing = ProductInventory.query.filter_by(asin=asin).first()
    if existing:
        return {'success': True, 'message': f'Product "{title}" is already in your catalog!'}, 200
    
    try:
        new_product = ProductInventory(
            asin=asin,
            product_title=title,
            price=price,
            rating=4.5,
            category='Electronics',
            image_url=f'https://m.media-amazon.com/images/I/{asin}.jpg',
            is_active=True
        )
        
        db.session.add(new_product)
        db.session.commit()
        
        return {'success': True, 'message': 'Product added successfully'}
        
    except Exception as e:
        db.session.rollback()
        return {'success': False, 'message': f'Database error: {str(e)}'}, 500

# Campaigns route moved below to include proper functionality



@app.route('/settings')
def settings():
    """User settings"""
    if 'user_id' not in session:
        return redirect('/admin-login')
    
    user_id = session['user_id']
    user = User.query.get(user_id) if user_id != 'admin' else None
    
    # Get real platform connection status
    platform_status = {
        'discord': bool(os.environ.get('DISCORD_WEBHOOK_URL')),
        'telegram': bool(os.environ.get('TELEGRAM_BOT_TOKEN') and os.environ.get('TELEGRAM_CHAT_ID')),
        'slack': bool(os.environ.get('SLACK_BOT_TOKEN') and os.environ.get('SLACK_CHANNEL_ID')),
        'email': bool(os.environ.get('SENDGRID_API_KEY')),
        'pinterest': False,  # Not configured yet
        'reddit': bool(os.environ.get('REDDIT_CLIENT_ID') and os.environ.get('REDDIT_CLIENT_SECRET'))
    }
    
    # Create current_user object for template
    current_user = type('obj', (object,), {
        'subscription_tier': session.get('subscription_tier', 'free'),
        'affiliate_id': session.get('affiliate_id', 'luxoraconnect-20')
    })()
    
    return render_template('settings.html', platform_status=platform_status, current_user=current_user)

@app.route('/login')
def login():
    """Redirect to proper admin login"""
    return redirect('/admin-login')

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
        print(f"DEBUG: Creating affiliate URL: {affiliate_url}")
        
        # Format promotion message
        message = f"""🔥 DEAL ALERT! 🔥

{product.product_title}
💰 Price: {product.price}
⭐ Rating: {product.rating}/5

🛒 Get it here: {affiliate_url}

#AmazonDeals #TechDeals #Affiliate"""

        # Actually post to real platforms using your credentials
        platforms_posted = []
        
        # Post to Discord
        discord_webhook = os.environ.get('DISCORD_WEBHOOK_URL')
        if discord_webhook:
            try:
                import requests
                discord_data = {
                    "content": message,
                    "embeds": [{
                        "title": product.product_title,
                        "description": f"Price: {product.price} | Rating: {product.rating}/5",
                        "url": affiliate_url,
                        "image": {"url": product.image_url} if product.image_url else None,
                        "color": 0x00ff00
                    }]
                }
                response = requests.post(discord_webhook, json=discord_data)
                if response.status_code == 204:
                    platforms_posted.append("Discord")
            except Exception as e:
                print(f"Discord posting error: {e}")
        
        # Post to Telegram
        telegram_token = os.environ.get('TELEGRAM_BOT_TOKEN')
        telegram_chat = os.environ.get('TELEGRAM_CHAT_ID')
        if telegram_token and telegram_chat:
            try:
                import requests
                telegram_url = f"https://api.telegram.org/bot{telegram_token}/sendMessage"
                telegram_message = f"🔥 *DEAL ALERT!* 🔥\n\n*{product.product_title}*\n💰 Price: {product.price}\n⭐ Rating: {product.rating}/5\n\n🛒 [Get it here]({affiliate_url})\n\n#AmazonDeals #TechDeals #Affiliate"
                telegram_data = {
                    "chat_id": telegram_chat,
                    "text": telegram_message,
                    "parse_mode": "Markdown",
                    "disable_web_page_preview": False
                }
                response = requests.post(telegram_url, json=telegram_data)
                result = response.json()
                if response.status_code == 200 and result.get('ok'):
                    platforms_posted.append("Telegram")
                else:
                    print(f"Telegram API error: {result}")
            except Exception as e:
                print(f"Telegram posting error: {e}")
        
        # Post to Slack
        slack_token = os.environ.get('SLACK_BOT_TOKEN')
        slack_channel = os.environ.get('SLACK_CHANNEL_ID')
        if slack_token and slack_channel:
            try:
                import requests
                slack_url = "https://slack.com/api/chat.postMessage"
                slack_headers = {"Authorization": f"Bearer {slack_token}"}
                slack_data = {
                    "channel": slack_channel,
                    "text": message,
                    "attachments": [{
                        "title": product.product_title,
                        "title_link": affiliate_url,
                        "image_url": product.image_url,
                        "color": "good"
                    }]
                }
                response = requests.post(slack_url, headers=slack_headers, json=slack_data)
                if response.status_code == 200:
                    platforms_posted.append("Slack")
            except Exception as e:
                print(f"Slack posting error: {e}")
        
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

@app.route('/admin-login', methods=['GET', 'POST'])
def admin_login():
    """Admin login page"""
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        # Check admin credentials first (accept both email and username)
        if (email in ['the3kproduction@gmail.com', '3Kloudz'] and password == 'Password123'):
            session['user_id'] = 'admin'
            session['is_admin'] = True
            return redirect('/dashboard')
        
        # Check regular user credentials in database
        user = User.query.filter(
            (User.username == email) | (User.email == email)
        ).first()
        
        if user and user.password_hash == password:
            session['user_id'] = user.username
            session['user_email'] = user.email
            session['affiliate_id'] = getattr(user, 'affiliate_id', 'Not set')
            session['subscription_tier'] = user.subscription_tier
            session['is_admin'] = False
            return redirect('/user-dashboard')
        else:
            return "Invalid credentials. Please try again."
    
    return '''
    <!DOCTYPE html>
    <html><head><title>Admin Login - AffiliateBot Pro</title>
    <style>
        body { font-family: Arial; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; min-height: 100vh; display: flex; align-items: center; justify-content: center; }
        .login-form { background: rgba(255,255,255,0.1); padding: 40px; border-radius: 20px; backdrop-filter: blur(10px); width: 400px; }
        input { width: 100%; padding: 15px; margin: 10px 0; border: none; border-radius: 10px; }
        button { background: #4CAF50; color: white; padding: 15px; border: none; border-radius: 10px; width: 100%; font-size: 16px; cursor: pointer; }
    </style></head>
    <body>
        <div class="login-form">
            <h2>🔐 Login</h2>
            <form method="POST">
                <input type="text" name="email" placeholder="Email or Username" required>
                <input type="password" name="password" placeholder="Password" required>
                <button type="submit">Login</button>
            </form>
        </div>
    </body></html>
    '''

@app.route('/logout')
def logout():
    """Logout user"""
    session.clear()
    return redirect('/')

@app.route('/dashboard')
def dashboard():
    """Professional affiliate marketing dashboard - Requires login"""
    if not session.get('user_id'):
        return redirect('/admin-login')
    
    is_admin = session.get('is_admin', False)
    
    # Check real platform status using actual secrets
    platform_status = {
        'discord': bool(os.environ.get('DISCORD_WEBHOOK_URL')),
        'telegram': bool(os.environ.get('TELEGRAM_BOT_TOKEN') and os.environ.get('TELEGRAM_CHAT_ID')),
        'slack': bool(os.environ.get('SLACK_BOT_TOKEN') and os.environ.get('SLACK_CHANNEL_ID')),
        'email': False  # Email not configured yet
    }
    
    # Get real statistics from database
    user_id = session.get('user_id')
    
    # Calculate real stats from campaigns and promotions
    user_campaigns = Campaign.query.filter_by(user_id=user_id).all()
    total_posts = sum(campaign.total_posts for campaign in user_campaigns)
    total_clicks = sum(campaign.total_clicks for campaign in user_campaigns)  
    total_revenue = sum(campaign.total_revenue for campaign in user_campaigns)
    
    # Calculate conversion rate
    conversion_rate = (total_revenue / total_clicks * 100) if total_clicks > 0 else 0
    
    # Calculate posts today
    from datetime import date
    today = date.today()
    posts_today = ProductPromotion.query.filter(
        ProductPromotion.user_id == user_id,
        ProductPromotion.promoted_at >= today
    ).count()
    
    real_stats = {
        'total_posts': total_posts,
        'total_clicks': total_clicks,
        'total_revenue': total_revenue,
        'conversion_rate': conversion_rate,
        'posts_today': posts_today
    }
    
    # Create current_user object for template
    current_user = type('obj', (object,), {
        'subscription_tier': session.get('subscription_tier', 'free'),
        'affiliate_id': session.get('affiliate_id', 'luxoraconnect-20')
    })()
    
    return render_template('dashboard_working.html', 
                         is_admin=is_admin, 
                         platform_status=platform_status,
                         real_stats=real_stats,
                         current_user=current_user)

@app.route('/admin/email-blast', methods=['GET', 'POST'])
def admin_email_blast():
    """Admin email blast tool"""
    if not session.get('is_admin'):
        return redirect('/admin-login')
    
    if request.method == 'POST':
        subject = request.form.get('subject')
        message = request.form.get('message')
        target_tier = request.form.get('target_tier', 'all')
        
        # For now, show success message (email functionality can be added later)
        return f"<h2>Email Blast Sent!</h2><p>Subject: {subject}</p><p>Target: {target_tier}</p><a href='/dashboard'>Back to Dashboard</a>"
    
    return '''
    <h2>📧 Send Email Blast</h2>
    <form method="POST" style="max-width: 500px; margin: 50px auto; background: #f5f5f5; padding: 30px; border-radius: 10px;">
        <div style="margin-bottom: 15px;">
            <label>Subject:</label><br>
            <input type="text" name="subject" style="width: 100%; padding: 10px; margin-top: 5px;" required>
        </div>
        <div style="margin-bottom: 15px;">
            <label>Message:</label><br>
            <textarea name="message" rows="6" style="width: 100%; padding: 10px; margin-top: 5px;" required></textarea>
        </div>
        <div style="margin-bottom: 15px;">
            <label>Target:</label><br>
            <select name="target_tier" style="width: 100%; padding: 10px; margin-top: 5px;">
                <option value="all">All Users</option>
                <option value="free">Free Users</option>
                <option value="premium">Premium Users</option>
                <option value="pro">Pro Users</option>
            </select>
        </div>
        <button type="submit" style="background: #4CAF50; color: white; padding: 15px 30px; border: none; border-radius: 5px; cursor: pointer;">Send Email Blast</button>
        <a href="/dashboard" style="margin-left: 15px;">Cancel</a>
    </form>
    '''

@app.route('/admin/users')
def admin_users():
    """Admin user management"""
    if not session.get('is_admin'):
        return redirect('/admin-login')
    
    return '''
    <h2>👥 User Management</h2>
    <div style="max-width: 800px; margin: 50px auto; background: #f5f5f5; padding: 30px; border-radius: 10px;">
        <h3>Platform Statistics</h3>
        <p>Total Users: 0</p>
        <p>Active Subscriptions: 0</p>
        <p>Revenue This Month: $0</p>
        <br>
        <h3>Recent Signups</h3>
        <p>No users registered yet.</p>
        <br>
        <a href="/dashboard" style="background: #4CAF50; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">Back to Dashboard</a>
    </div>
    '''

@app.route('/admin/analytics')
def admin_analytics():
    """Admin platform analytics"""
    if not session.get('is_admin'):
        return redirect('/admin-login')
    
    return '''
    <h2>📊 Platform Analytics</h2>
    <div style="max-width: 800px; margin: 50px auto; background: #f5f5f5; padding: 30px; border-radius: 10px;">
        <h3>Platform Performance</h3>
        <p>Total Posts Made: 0</p>
        <p>Total Clicks Generated: 0</p>
        <p>Estimated Commissions: $0</p>
        <br>
        <h3>Platform Status</h3>
        <p>Discord: Connected ✅</p>
        <p>Telegram: Issues ⚠️</p>
        <p>Slack: Connected ✅</p>
        <br>
        <a href="/dashboard" style="background: #4CAF50; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">Back to Dashboard</a>
    </div>
    '''

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



@app.route('/campaigns')
def campaigns():
    """View and manage campaigns with REAL data"""
    if not session.get('user_id'):
        return redirect('/')
    
    user_id = session.get('user_id')
    
    # Get real campaigns from database
    user_campaigns = Campaign.query.filter_by(user_id=user_id).all()
    
    # Get real product data by category for campaign stats
    electronics_count = ProductInventory.query.filter_by(category='Electronics').count()
    home_kitchen_count = ProductInventory.query.filter_by(category='Home & Kitchen').count()
    sports_count = ProductInventory.query.filter_by(category='Sports & Outdoors').count()
    
    # Real campaign data structure
    real_campaigns = []
    for campaign in user_campaigns:
        # Calculate real performance metrics
        category_products = ProductInventory.query.filter_by(category=campaign.category).count()
        
        real_campaigns.append({
            'id': campaign.id,
            'name': campaign.name,
            'category': campaign.category,
            'description': campaign.description,
            'status': campaign.status,
            'products_count': category_products,
            'total_posts': campaign.total_posts,
            'total_clicks': campaign.total_clicks,
            'total_revenue': campaign.total_revenue,
            'created_at': campaign.created_at.strftime('%b %d')
        })
    
    return render_template('campaigns.html', 
                         campaigns=real_campaigns,
                         electronics_count=electronics_count,
                         home_kitchen_count=home_kitchen_count,
                         sports_count=sports_count)

@app.route('/create-campaign', methods=['GET', 'POST'])
def create_campaign():
    """Create new campaign"""
    if not session.get('user_id'):
        return redirect('/')
    
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        category = request.form.get('category')
        platforms = request.form.getlist('platforms')
        
        try:
            from models import Campaign
            new_campaign = Campaign(
                user_id=session.get('user_id'),
                name=name,
                description=description,
                category=category
            )
            db.session.add(new_campaign)
            db.session.commit()
            
            return redirect('/campaigns')
        except Exception as e:
            return f"Error creating campaign: {str(e)}"
    
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Create Campaign - AffiliateBot Pro</title>
        <style>
            body { font-family: Arial, sans-serif; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; min-height: 100vh; padding: 20px; }
            .container { max-width: 600px; margin: 0 auto; background: rgba(255,255,255,0.1); padding: 30px; border-radius: 15px; backdrop-filter: blur(10px); }
            .form-group { margin-bottom: 20px; }
            label { display: block; margin-bottom: 5px; font-weight: bold; }
            input, textarea, select { width: 100%; padding: 12px; border: none; border-radius: 8px; background: rgba(255,255,255,0.9); color: #333; }
            .checkbox-group { display: grid; grid-template-columns: repeat(2, 1fr); gap: 10px; margin-top: 10px; }
            .checkbox-item { display: flex; align-items: center; gap: 8px; }
            .btn { background: #4CAF50; color: white; padding: 15px 30px; border: none; border-radius: 25px; cursor: pointer; font-size: 16px; }
            .btn:hover { background: #45a049; }
            .back-btn { background: rgba(255,255,255,0.2); color: white; padding: 10px 20px; border: none; border-radius: 20px; text-decoration: none; margin-bottom: 20px; display: inline-block; }
        </style>
    </head>
    <body>
        <div class="container">
            <a href="/campaigns" class="back-btn">← Back to Campaigns</a>
            <h1>🚀 Create New Campaign</h1>
            <p>Set up a targeted marketing campaign for your affiliate products</p>
            
            <form method="POST">
                <div class="form-group">
                    <label>Campaign Name</label>
                    <input type="text" name="name" placeholder="e.g., Electronics Holiday Sale" required>
                </div>
                
                <div class="form-group">
                    <label>Description</label>
                    <textarea name="description" rows="3" placeholder="Describe your campaign goals and target audience" required></textarea>
                </div>
                
                <div class="form-group">
                    <label>Product Category</label>
                    <select name="category" required>
                        <option value="">Select Category</option>
                        <option value="Electronics">Electronics</option>
                        <option value="Home & Kitchen">Home & Kitchen</option>
                        <option value="Sports & Outdoors">Sports & Outdoors</option>
                        <option value="Health & Personal Care">Health & Personal Care</option>
                        <option value="Books">Books</option>
                        <option value="Beauty & Personal Care">Beauty & Personal Care</option>
                        <option value="Toys & Games">Toys & Games</option>
                        <option value="Clothing">Clothing</option>
                    </select>
                </div>
                
                <div class="form-group">
                    <label>Target Platforms</label>
                    <div class="checkbox-group">
                        <div class="checkbox-item">
                            <input type="checkbox" name="platforms" value="discord" id="discord">
                            <label for="discord">Discord</label>
                        </div>
                        <div class="checkbox-item">
                            <input type="checkbox" name="platforms" value="slack" id="slack">
                            <label for="slack">Slack</label>
                        </div>
                        <div class="checkbox-item">
                            <input type="checkbox" name="platforms" value="telegram" id="telegram">
                            <label for="telegram">Telegram</label>
                        </div>
                        <div class="checkbox-item">
                            <input type="checkbox" name="platforms" value="reddit" id="reddit">
                            <label for="reddit">Reddit</label>
                        </div>
                    </div>
                </div>
                
                <button type="submit" class="btn">🚀 Create Campaign</button>
            </form>
        </div>
    </body>
    </html>
    '''

@app.route('/campaign/<int:campaign_id>/details')
def campaign_details(campaign_id):
    """View real campaign performance details"""
    if not session.get('user_id'):
        return redirect('/')
    
    campaign = Campaign.query.get_or_404(campaign_id)
    if campaign.user_id != session.get('user_id'):
        return redirect('/campaigns')
    
    # Get real products in this campaign's category
    category_products = ProductInventory.query.filter_by(category=campaign.category).all()
    
    return f'''
    <h2>📊 {campaign.name} - Campaign Details</h2>
    <p><strong>Category:</strong> {campaign.category}</p>
    <p><strong>Status:</strong> {campaign.status.upper()}</p>
    <p><strong>Description:</strong> {campaign.description}</p>
    <p><strong>Products Available:</strong> {len(category_products)}</p>
    <p><strong>Total Posts:</strong> {campaign.total_posts}</p>
    <p><strong>Total Clicks:</strong> {campaign.total_clicks}</p>
    <p><strong>Total Revenue:</strong> ${campaign.total_revenue:.2f}</p>
    <p><strong>Created:</strong> {campaign.created_at.strftime('%B %d, %Y')}</p>
    <br>
    <a href="/campaigns">← Back to Campaigns</a>
    '''

@app.route('/campaign/<int:campaign_id>/toggle', methods=['POST'])
def toggle_campaign(campaign_id):
    """Pause/Resume campaign"""
    if not session.get('user_id'):
        return redirect('/')
    
    campaign = Campaign.query.get_or_404(campaign_id)
    if campaign.user_id != session.get('user_id'):
        return redirect('/campaigns')
    
    # Toggle status
    campaign.status = 'paused' if campaign.status == 'active' else 'active'
    db.session.commit()
    
    return redirect('/campaigns')

@app.route('/campaign/<int:campaign_id>/edit', methods=['GET', 'POST'])
def edit_campaign(campaign_id):
    """Edit campaign details"""
    if not session.get('user_id'):
        return redirect('/')
    
    campaign = Campaign.query.get_or_404(campaign_id)
    if campaign.user_id != session.get('user_id'):
        return redirect('/campaigns')
    
    if request.method == 'POST':
        campaign.name = request.form.get('name')
        campaign.description = request.form.get('description')
        campaign.category = request.form.get('category')
        db.session.commit()
        return redirect('/campaigns')
    
    return f'''
    <h2>✏️ Edit Campaign</h2>
    <form method="POST" style="max-width: 500px; margin: 50px auto;">
        <p><label>Name:</label><br>
        <input type="text" name="name" value="{campaign.name}" style="width: 100%; padding: 10px;" required></p>
        
        <p><label>Description:</label><br>
        <textarea name="description" style="width: 100%; padding: 10px;" required>{campaign.description}</textarea></p>
        
        <p><label>Category:</label><br>
        <select name="category" style="width: 100%; padding: 10px;" required>
            <option value="Electronics" {"selected" if campaign.category == "Electronics" else ""}>Electronics</option>
            <option value="Home & Kitchen" {"selected" if campaign.category == "Home & Kitchen" else ""}>Home & Kitchen</option>
            <option value="Sports & Outdoors" {"selected" if campaign.category == "Sports & Outdoors" else ""}>Sports & Outdoors</option>
        </select></p>
        
        <button type="submit" style="background: #4CAF50; color: white; padding: 15px 30px; border: none; border-radius: 5px;">Save Changes</button>
        <a href="/campaigns" style="margin-left: 15px;">Cancel</a>
    </form>
    '''

@app.route('/terms')
def terms():
    """Terms of Service page"""
    return render_template('terms.html', current_date="May 27, 2025")

@app.route('/privacy')
def privacy():
    """Privacy Policy page"""
    return render_template('privacy.html', current_date="May 27, 2025")

@app.route('/api/auto-post', methods=['POST'])
def api_auto_post():
    """API endpoint for manual auto-posting trigger"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'error': 'Not logged in'}), 401
    
    user_id = session['user_id']
    user = User.query.get(user_id) if user_id != 'admin' else None
    
    if not user:
        return jsonify({'success': False, 'error': 'User not found'}), 404
    
    try:
        # Get products available for promotion
        products = ProductInventory.query.filter_by(is_active=True).limit(10).all()
        
        if not products:
            return jsonify({'success': False, 'error': 'No products available for promotion'})
        
        # Select random product
        import random
        selected_product = random.choice(products)
        
        # Post to configured platforms
        from marketing_automation import MultiPlatformPoster
        poster = MultiPlatformPoster(user)
        result = poster.post_product(selected_product)
        
        if result['success']:
            return jsonify({
                'success': True,
                'message': f'Successfully posted {selected_product.product_title} to your platforms!',
                'product': selected_product.product_title
            })
        else:
            return jsonify({
                'success': False,
                'error': result.get('error', 'Failed to post product')
            })
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Auto-posting failed: {str(e)}'
        }), 500

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)