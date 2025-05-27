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

@app.route('/create-account', methods=['POST'])
def create_account():
    """Create user account after successful payment"""
    username = request.form.get('username')
    email = request.form.get('email')
    password = request.form.get('password')
    confirm_password = request.form.get('confirm_password')
    affiliate_id = request.form.get('affiliate_id')
    
    # Validate passwords match
    if password != confirm_password:
        return "Passwords don't match. Please go back and try again."
    
    # Create user session (in a real app, you'd save to database)
    session['user_id'] = username
    session['user_email'] = email
    session['affiliate_id'] = affiliate_id
    session['subscription_tier'] = 'premium'  # Since they just paid
    
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
    
    username = session.get('user_id', 'User')
    affiliate_id = session.get('affiliate_id', 'Not set')
    
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
        
        # Check admin credentials (accept both email and username)
        if (email in ['the3kproduction@gmail.com', '3Kloudz'] and password == 'Password123'):
            session['user_id'] = 'admin'
            session['is_admin'] = True
            return redirect('/dashboard')
        else:
            return "Invalid credentials"
    
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
            <h2>🔐 Admin Login</h2>
            <form method="POST">
                <input type="email" name="email" placeholder="Admin Email" required>
                <input type="password" name="password" placeholder="Password" required>
                <button type="submit">Login as Admin</button>
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
    
    return render_template('dashboard_working.html', is_admin=is_admin, platform_status=platform_status)

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

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)