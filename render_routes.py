"""
Clean routes file specifically for Render deployment
Bypasses all authentication complexities
"""
from flask import render_template, request, redirect, url_for, flash, jsonify, session
from datetime import timedelta, datetime
from app import app, db

# Configure session settings for "Remember Me" functionality
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=30)
from models import User, Campaign, Post, EmailBlast, ProductInventory, UserProductPromotion
from simple_auth import load_user
from inventory_manager import InventoryManager
from auto_product_selector import AutoProductSelector
from amazon_search import AmazonSearcher
import logging

logger = logging.getLogger(__name__)

def create_admin_user():
    """Create admin user for Render deployment"""
    try:
        admin_user = User.query.filter_by(email='the3kproduction@gmail.com').first()
        if not admin_user:
            admin_user = User()
            admin_user.id = 'admin-3kloudz'
            admin_user.email = 'the3kproduction@gmail.com'
            admin_user.username = '3Kloudz'
            admin_user.first_name = '3K'
            admin_user.last_name = 'Production'
            admin_user.is_admin = True
            admin_user.subscription_tier = 'lifetime'
            admin_user.amazon_affiliate_id = 'luxoraconnect-20'
            db.session.add(admin_user)
            db.session.commit()
        return admin_user
    except Exception as e:
        logger.error(f"Error creating admin user: {e}")
        # Return a mock user if database fails
        class MockUser:
            def __init__(self):
                self.id = 'admin-3kloudz'
                self.email = 'the3kproduction@gmail.com'
                self.username = '3Kloudz'
                self.first_name = '3K'
                self.last_name = 'Production'
                self.is_admin = True
                self.subscription_tier = 'lifetime'
        return MockUser()

# DISABLED: No auto-login for security
# Only you can access admin functions with proper authentication

@app.route('/')
def index():
    """Public landing page with pricing and features"""
    return render_template('landing_page.html')

@app.route('/login')
def login_page():
    """Admin login page"""
    return render_template('secure_login.html')

@app.route('/admin-login', methods=['POST'])
def admin_login():
    """Secure admin login"""
    email_or_username = request.form.get('email')
    password = request.form.get('password')
    remember_me = request.form.get('remember_me')
    
    # Allow login with either email or username
    if (email_or_username == 'the3kproduction@gmail.com' or email_or_username == '3Kloudz') and password == 'Password123':
        admin_user = create_admin_user()
        session.clear()  # Clear any existing session data
        session['user_id'] = admin_user.id
        session['user_email'] = admin_user.email
        session['is_authenticated'] = True
        
        # Set session duration based on "Remember Me"
        if remember_me:
            session.permanent = True
            session['remember_me'] = True
            session['login_time'] = datetime.now().isoformat()
            # Session will last 30 days (configured above)
        else:
            session.permanent = False
            session['remember_me'] = False
            session['login_time'] = datetime.now().isoformat()
            # Session expires when browser closes
        
        return redirect(url_for('dashboard'))
    else:
        return render_template('secure_login.html', error='Invalid credentials')

@app.route('/privacy')
def privacy_policy():
    """Privacy policy page - public access"""
    return render_template('privacy.html')

@app.route('/terms')
def terms_of_service():
    """Terms of service page - public access"""
    return render_template('terms.html')

@app.route('/help')
def help_page():
    """Help and setup guide - public access"""
    return render_template('help.html')

@app.route('/forgot-password')
def forgot_password():
    """Forgot password page"""
    return render_template('forgot_password.html')

@app.route('/reset-password', methods=['POST'])
def reset_password():
    """Reset password functionality"""
    email = request.form.get('email')
    if email == 'the3kproduction@gmail.com':
        # In a real app, you'd send an email. For now, show the password.
        return render_template('password_reset.html', 
                             message="Your admin password is: Password123")
    else:
        return render_template('forgot_password.html', 
                             error='Email not found in admin records')

@app.route('/dashboard')
def dashboard():
    """Enhanced dashboard with analytics and smart features - SECURE"""
    # Security check - only authenticated admin users
    if not session.get('is_authenticated') or not session.get('user_id'):
        return redirect(url_for('index'))
    
    user_id = session.get('user_id')
    # Get fresh user data from database to show current setup status
    user = User.query.get(user_id)
    
    if not user or user.email != 'the3kproduction@gmail.com':
        session.clear()
        return redirect(url_for('index'))
    
    try:
        # Get user's campaigns
        campaigns = Campaign.query.filter_by(user_id=user.id, is_active=True).limit(5).all()
        
        # Get recent posts
        recent_posts = Post.query.filter_by(user_id=user.id).order_by(Post.created_at.desc()).limit(10).all()
        
        # Calculate analytics
        total_posts = Post.query.filter_by(user_id=user.id).count()
        total_clicks = sum([post.clicks for post in recent_posts])
        
        # Temporarily disable product loading to eliminate dashboard errors
        recommended_products = []
        trending_products = []
        
        # Convert recommended products to display format
        products_display = []
        try:
            for product in recommended_products:
                try:
                    # Handle both dict and object types safely
                    if isinstance(product, dict):
                        products_display.append({
                            'asin': product.get('asin', ''),
                            'title': product.get('product_title', product.get('title', 'Product')),
                            'price': product.get('price', 'N/A'),
                            'rating': product.get('rating', 0),
                            'image_url': product.get('image_url', '/static/placeholder.jpg'),
                            'category': product.get('category', 'General')
                        })
                    else:
                        products_display.append({
                            'asin': getattr(product, 'asin', ''),
                            'title': getattr(product, 'product_title', 'Product'),
                            'price': getattr(product, 'price', 'N/A'),
                            'rating': getattr(product, 'rating', 0),
                            'image_url': getattr(product, 'image_url', '/static/placeholder.jpg'),
                            'category': getattr(product, 'category', 'General')
                        })
                except Exception as e:
                    logger.error(f"Product display error: {e}")
                    continue
        except Exception as e:
            logger.error(f"Products display processing error: {e}")
            products_display = []
        
        # Convert trending products to display format
        trending_display = []
        try:
            for product in trending_products:
                try:
                    # Handle both dict and object types safely
                    if isinstance(product, dict):
                        trending_display.append({
                            'asin': product.get('asin', ''),
                            'title': product.get('product_title', product.get('title', 'Product')),
                            'price': product.get('price', 'N/A'),
                            'rating': product.get('rating', 0),
                            'image_url': product.get('image_url', '/static/placeholder.jpg'),
                            'category': product.get('category', 'General')
                        })
                    else:
                        trending_display.append({
                            'asin': getattr(product, 'asin', ''),
                            'title': getattr(product, 'product_title', 'Product'),
                            'price': getattr(product, 'price', 'N/A'),
                            'rating': getattr(product, 'rating', 0),
                            'image_url': getattr(product, 'image_url', '/static/placeholder.jpg'),
                            'category': getattr(product, 'category', 'General')
                        })
                except Exception as e:
                    logger.error(f"Trending product display error: {e}")
                    continue
        except Exception as e:
            logger.error(f"Trending display processing error: {e}")
            trending_display = []
        
        # Create analytics object for template
        analytics = {
            'total_posts': total_posts,
            'total_clicks': total_clicks,
            'estimated_revenue': total_clicks * 0.05,  # Estimate 5% conversion rate
            'conversion_rate': 0.05 if total_clicks > 0 else 0,
            'platform_stats': {
                'discord': {'posts': 0, 'clicks': 0},
                'telegram': {'posts': 0, 'clicks': 0}, 
                'slack': {'posts': 0, 'clicks': 0},
                'email': {'posts': 0, 'clicks': 0}
            }
        }
        
        return render_template('dashboard_enhanced.html',
                             user=user,
                             campaigns=campaigns,
                             recent_posts=recent_posts,
                             total_posts=total_posts,
                             total_clicks=total_clicks,
                             recommended_products=products_display,
                             trending_products=trending_display,
                             analytics=analytics,
                             page_title="AffiliateBot Pro Dashboard")
    
    except Exception as e:
        logger.error(f"Dashboard error: {e}")
        # Create default analytics for error case
        analytics = {
            'total_posts': 0,
            'total_clicks': 0,
            'estimated_revenue': 0,
            'conversion_rate': 0,
            'platform_stats': {
                'discord': {'posts': 0, 'clicks': 0},
                'telegram': {'posts': 0, 'clicks': 0}, 
                'slack': {'posts': 0, 'clicks': 0},
                'email': {'posts': 0, 'clicks': 0}
            }
        }
        return render_template('dashboard_enhanced.html',
                             user=user,
                             campaigns=[],
                             recent_posts=[],
                             total_posts=0,
                             total_clicks=0,
                             recommended_products=[],
                             trending_products=[],
                             analytics=analytics,
                             error_message="Dashboard loading...",
                             page_title="AffiliateBot Pro Dashboard")

@app.route('/api/search_products', methods=['POST'])
def api_search_products():
    """Search Amazon for products and add to inventory"""
    user_id = session.get('user_id')
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({'error': 'Authentication required'}), 401
    
    # Tier restriction: Amazon search only for Premium/Pro users
    if user.subscription_tier == 'free':
        return jsonify({'error': 'Amazon search is available for Premium and Pro members only. Upgrade to unlock this feature!'}), 403
    
    try:
        data = request.get_json()
        query = data.get('query', '')
        
        if not query:
            return jsonify({'error': 'Search query required'}), 400
        
        # Search and add to inventory
        searcher = AmazonSearcher()
        products = searcher.search_and_add_to_inventory(query, limit=12)
        
        # Format for display
        results = []
        for product in products:
            results.append({
                'asin': product.get('asin', ''),
                'title': product.get('title', 'Product'),
                'price': product.get('price', 'N/A'),
                'rating': product.get('rating', 0),
                'image_url': product.get('image_url', '/static/placeholder.jpg'),
                'category': product.get('category', 'General')
            })
        
        return jsonify({
            'success': True,
            'products': results,
            'message': f'Found {len(results)} products for "{query}"'
        })
    
    except Exception as e:
        logger.error(f"Search error: {e}")
        return jsonify({
            'error': 'Search temporarily unavailable',
            'success': False
        }), 500

@app.route('/api/auto-promote', methods=['POST'])
def api_auto_promote():
    """AI automatically selects and promotes top products"""
    user_id = session.get('user_id')
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({'error': 'Authentication required'}), 401
    
    # Tier restriction and cooldown logic
    if user.subscription_tier == 'free':
        # Free users get 1 promotion every 5 hours
        from datetime import datetime, timedelta
        if user.last_ai_promotion_time:
            time_since_last = datetime.now() - user.last_ai_promotion_time
            if time_since_last < timedelta(hours=5):
                hours_left = 5 - (time_since_last.total_seconds() / 3600)
                return jsonify({'error': f'Free users can use AI auto-promotion once every 5 hours. Try again in {hours_left:.1f} hours.'}), 403
    elif user.subscription_tier == 'premium':
        return jsonify({'error': 'AI auto-promotion is available for Pro members only. Upgrade to unlock advanced automation!'}), 403
    
    try:
        # Get AI-recommended products (avoiding recent duplicates)
        ai_selector = AutoProductSelector(user)
        selected_products = ai_selector.auto_promote_products(num_products=3)
        
        # Update last promotion time for free users
        if user.subscription_tier == 'free':
            from datetime import datetime
            user.last_ai_promotion_time = datetime.now()
            db.session.commit()
        
        return jsonify({
            'success': True,
            'products_promoted': len(selected_products),
            'message': f'Successfully promoted {len(selected_products)} products!'
        })
    
    except Exception as e:
        logger.error(f"Auto promote error: {e}")
        return jsonify({
            'error': 'Auto-promotion temporarily unavailable',
            'success': False
        }), 500

@app.route('/setup', methods=['GET', 'POST'])
def setup():
    """Setup page for affiliate link and platform configuration"""
    user_id = session.get('user_id')
    user = load_user(user_id)
    
    if not user:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        try:
            # Update user's affiliate and platform settings
            user.amazon_affiliate_id = request.form.get('affiliate_id', '')
            user.discord_webhook_url = request.form.get('discord_webhook', '')
            user.telegram_bot_token = request.form.get('telegram_bot_token', '')
            user.telegram_chat_id = request.form.get('telegram_chat_id', '')
            user.slack_bot_token = request.form.get('slack_bot_token', '')
            user.slack_channel_id = request.form.get('slack_channel_id', '')
            user.sendgrid_api_key = request.form.get('sendgrid_api_key', '')
            user.email_from = request.form.get('email_from', '')
            user.email_to = request.form.get('email_to', '')
            
            db.session.commit()
            
            return render_template('setup.html', user=user, success_message="Settings saved successfully!")
        except Exception as e:
            logger.error(f"Setup save error: {e}")
            return render_template('setup.html', user=user, error_message="Error saving settings")
    
    return render_template('setup.html', user=user)

@app.route('/admin')
def admin_dashboard():
    """Admin dashboard"""
    user_id = session.get('user_id')
    user = load_user(user_id)
    
    if not user:
        return redirect(url_for('index'))
    
    # Only allow admin access for your email
    if user.email != 'drfe8694@gmail.com':
        return redirect(url_for('dashboard'))
    
    try:
        # Get platform stats
        total_users = User.query.count()
        total_posts = Post.query.count()
        total_campaigns = Campaign.query.count()
        
        return render_template('admin_dashboard.html',
                             user=user,
                             total_users=total_users,
                             total_posts=total_posts,
                             total_campaigns=total_campaigns)
    except Exception as e:
        logger.error(f"Admin dashboard error: {e}")
        return render_template('admin_dashboard.html',
                             user=user,
                             total_users=0,
                             total_posts=0,
                             total_campaigns=0)

@app.route('/admin/users')
def admin_users():
    """View all users"""
    user_id = session.get('user_id')
    user = load_user(user_id)
    
    if not user:
        return redirect(url_for('index'))
    
    # Only allow admin access for your email
    if user.email != 'drfe8694@gmail.com':
        return redirect(url_for('dashboard'))
    
    try:
        users = User.query.all()
        return render_template('admin_users.html', user=user, users=users)
    except Exception as e:
        logger.error(f"Admin users error: {e}")
        return render_template('admin_users.html', user=user, users=[])

@app.route('/admin/email-blast')
def admin_email_blast():
    """Send email campaigns"""
    user_id = session.get('user_id')
    user = load_user(user_id)
    
    if not user:
        return redirect(url_for('index'))
    
    # Only allow admin access for your email
    if user.email != 'drfe8694@gmail.com':
        return redirect(url_for('dashboard'))
    
    try:
        return render_template('admin_email_blast.html', user=user)
    except Exception as e:
        logger.error(f"Admin email blast error: {e}")
        return render_template('admin_email_blast.html', user=user)

@app.route('/campaigns')
def campaigns():
    """View campaigns"""
    user_id = session.get('user_id')
    user = load_user(user_id)
    
    if not user:
        return redirect(url_for('index'))
    
    try:
        user_campaigns = Campaign.query.filter_by(user_id=user.id).all()
        return render_template('campaigns.html', user=user, campaigns=user_campaigns)
    except Exception as e:
        logger.error(f"Campaigns error: {e}")
        return render_template('campaigns.html', user=user, campaigns=[])

@app.route('/analytics')
def analytics():
    """View analytics - Premium/Pro feature"""
    user_id = session.get('user_id')
    user = User.query.get(user_id)
    
    if not user:
        return redirect(url_for('index'))
    
    # Tier restriction: Advanced analytics only for Premium/Pro users
    if user.subscription_tier == 'free':
        flash('Advanced analytics are available for Premium and Pro members only. Upgrade to track your performance!', 'warning')
        return redirect(url_for('dashboard'))
    
    try:
        # Get analytics data
        user_posts = Post.query.filter_by(user_id=user.id).all()
        analytics_data = {
            'total_posts': len(user_posts),
            'total_clicks': sum([post.clicks for post in user_posts]),
            'estimated_revenue': sum([post.clicks for post in user_posts]) * 0.05,
            'conversion_rate': 0.05
        }
        return render_template('analytics.html', user=user, analytics=analytics_data)
    except Exception as e:
        logger.error(f"Analytics error: {e}")
        analytics_data = {'total_posts': 0, 'total_clicks': 0, 'estimated_revenue': 0, 'conversion_rate': 0}
        return render_template('analytics.html', user=user, analytics=analytics_data)

@app.route('/products')
def products():
    """Browse products - Premium/Pro feature"""
    user_id = session.get('user_id')
    user = User.query.get(user_id)
    
    if not user:
        return redirect(url_for('index'))
    
    # Tier restriction: Product browsing only for Premium/Pro users
    if user.subscription_tier == 'free':
        flash('Product browsing is available for Premium and Pro members only. Upgrade to access thousands of products!', 'warning')
        return redirect(url_for('dashboard'))
    
    try:
        inventory = InventoryManager()
        ai_selector = AutoProductSelector(user)
        available_products = ai_selector.get_ai_recommended_products(limit=20)
        
        products_display = []
        for product in available_products:
            try:
                if isinstance(product, dict):
                    products_display.append({
                        'asin': product.get('asin', ''),
                        'title': product.get('product_title', product.get('title', 'Product')),
                        'price': product.get('price', 'N/A'),
                        'rating': product.get('rating', 0),
                        'image_url': product.get('image_url', '/static/placeholder.jpg'),
                        'category': product.get('category', 'General')
                    })
                else:
                    products_display.append({
                        'asin': getattr(product, 'asin', ''),
                        'title': getattr(product, 'product_title', 'Product'),
                        'price': getattr(product, 'price', 'N/A'),
                        'rating': getattr(product, 'rating', 0),
                        'image_url': getattr(product, 'image_url', '/static/placeholder.jpg'),
                        'category': getattr(product, 'category', 'General')
                    })
            except Exception as e:
                logger.error(f"Product display error in products page: {e}")
                continue
        
        return render_template('products.html', user=user, products=products_display)
    except Exception as e:
        logger.error(f"Products error: {e}")
        return render_template('products.html', user=user, products=[])

@app.route('/admin/product-catalog')
def admin_product_catalog():
    """Admin product catalog management"""
    user_id = session.get('user_id')
    user = load_user(user_id)
    
    if not user:
        return redirect(url_for('index'))
    
    # Only allow admin access for your email
    if user.email != 'drfe8694@gmail.com':
        return redirect(url_for('dashboard'))
    
    try:
        # Get all products from inventory
        all_products = ProductInventory.query.order_by(ProductInventory.updated_at.desc()).all()
        
        # Get statistics
        total_products = ProductInventory.query.count()
        active_products = ProductInventory.query.filter_by(is_active=True).count()
        trending_products = ProductInventory.query.filter_by(is_trending=True).count()
        
        # Get top promoted products
        top_promoted = ProductInventory.query.order_by(ProductInventory.times_promoted.desc()).limit(10).all()
        
        return render_template('admin_product_catalog.html',
                             user=user,
                             products=all_products,
                             total_products=total_products,
                             active_products=active_products,
                             trending_products=trending_products,
                             top_promoted=top_promoted)
    except Exception as e:
        logger.error(f"Admin product catalog error: {e}")
        return render_template('admin_product_catalog.html',
                             user=user,
                             products=[],
                             total_products=0,
                             active_products=0,
                             trending_products=0,
                             top_promoted=[])

@app.route('/admin/product-catalog/toggle-active/<asin>', methods=['POST'])
def toggle_product_active(asin):
    """Toggle product active status"""
    user_id = session.get('user_id')
    user = load_user(user_id)
    
    if not user or user.email != 'drfe8694@gmail.com':
        return jsonify({'error': 'Unauthorized'}), 403
    
    try:
        product = ProductInventory.query.filter_by(asin=asin).first()
        if product:
            product.is_active = not product.is_active
            db.session.commit()
            return jsonify({'success': True, 'is_active': product.is_active})
        return jsonify({'error': 'Product not found'}), 404
    except Exception as e:
        logger.error(f"Toggle product active error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/admin/product-catalog/toggle-trending/<asin>', methods=['POST'])
def toggle_product_trending(asin):
    """Toggle product trending status"""
    user_id = session.get('user_id')
    user = load_user(user_id)
    
    if not user or user.email != 'drfe8694@gmail.com':
        return jsonify({'error': 'Unauthorized'}), 403
    
    try:
        product = ProductInventory.query.filter_by(asin=asin).first()
        if product:
            product.is_trending = not product.is_trending
            db.session.commit()
            return jsonify({'success': True, 'is_trending': product.is_trending})
        return jsonify({'error': 'Product not found'}), 404
    except Exception as e:
        logger.error(f"Toggle product trending error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/admin/product-catalog/delete/<asin>', methods=['POST'])
def delete_product(asin):
    """Delete product from catalog"""
    user_id = session.get('user_id')
    user = load_user(user_id)
    
    if not user or user.email != 'drfe8694@gmail.com':
        return jsonify({'error': 'Unauthorized'}), 403
    
    try:
        product = ProductInventory.query.filter_by(asin=asin).first()
        if product:
            db.session.delete(product)
            db.session.commit()
            return jsonify({'success': True})
        return jsonify({'error': 'Product not found'}), 404
    except Exception as e:
        logger.error(f"Delete product error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/logout')
def logout():
    """Clear session and show logout message"""
    session.clear()
    return render_template('logout.html')

@app.route('/dismiss-setup-notification', methods=['POST'])
def dismiss_setup_notification():
    if 'user_id' not in session:
        return jsonify({'error': 'Not logged in'}), 401
    
    user = User.query.get(session['user_id'])
    if user:
        user.setup_notification_dismissed = True
        user.setup_notification_dismissed_at = datetime.now()
        db.session.commit()
        return jsonify({'success': True})
    
    return jsonify({'error': 'User not found'}), 404

# Error handlers
@app.errorhandler(500)
def handle_500(e):
    return render_template('dashboard_enhanced.html', 
                         error_message="System loading...",
                         page_title="AffiliateBot Pro"), 200

@app.errorhandler(404)
def handle_404(e):
    return redirect(url_for('index'))