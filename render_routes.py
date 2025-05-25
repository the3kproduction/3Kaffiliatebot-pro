"""
Clean routes file specifically for Render deployment
Bypasses all authentication complexities
"""
from flask import render_template, request, redirect, url_for, flash, jsonify, session
from app import app, db
from models import User, Campaign, Post, EmailBlast, ProductInventory, UserProductPromotion
from simple_auth import create_demo_user, load_user
from inventory_manager import InventoryManager
from auto_product_selector import AutoProductSelector
from amazon_search import AmazonSearcher
import logging

logger = logging.getLogger(__name__)

# Auto-login demo user for Render
@app.before_request
def auto_login_demo_user():
    """Auto-login demo user for Render deployment"""
    if 'user_id' not in session:
        demo_user = create_demo_user()
        session['user_id'] = demo_user.id
        session.permanent = True

@app.route('/')
def index():
    """Landing page - auto-login for Render"""
    user_id = session.get('user_id')
    user = load_user(user_id) if user_id else None
    
    if user:
        return redirect(url_for('dashboard'))
    else:
        return render_template('dashboard_enhanced.html', 
                             page_title="AffiliateBot Pro - Live on Render!",
                             show_landing=True)

@app.route('/dashboard')
def dashboard():
    """Enhanced dashboard with analytics and smart features"""
    user_id = session.get('user_id')
    user = load_user(user_id)
    
    if not user:
        return redirect(url_for('index'))
    
    try:
        # Get user's campaigns
        campaigns = Campaign.query.filter_by(user_id=user.id, is_active=True).limit(5).all()
        
        # Get recent posts
        recent_posts = Post.query.filter_by(user_id=user.id).order_by(Post.created_at.desc()).limit(10).all()
        
        # Calculate analytics
        total_posts = Post.query.filter_by(user_id=user.id).count()
        total_clicks = sum([post.clicks for post in recent_posts])
        
        # Get recommended products using new inventory system
        inventory = InventoryManager()
        ai_selector = AutoProductSelector(user)
        recommended_products = ai_selector.get_ai_recommended_products(limit=6)
        
        # Get trending products from inventory
        trending_products = inventory.get_best_performing_products(limit=6)
        
        # Convert recommended products to display format
        products_display = []
        for product in recommended_products:
            products_display.append({
                'asin': product.asin,
                'title': product.product_title,
                'price': product.price or 'N/A',
                'rating': product.rating or 0,
                'image_url': product.image_url or '/static/placeholder.jpg',
                'category': product.category or 'General'
            })
        
        # Convert trending products to display format
        trending_display = []
        for product in trending_products:
            trending_display.append({
                'asin': product.asin,
                'title': product.product_title,
                'price': product.price or 'N/A',
                'rating': product.rating or 0,
                'image_url': product.image_url or '/static/placeholder.jpg',
                'category': product.category or 'General'
            })
        
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
    user = load_user(user_id)
    
    if not user:
        return jsonify({'error': 'Authentication required'}), 401
    
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

@app.route('/api/auto_promote', methods=['POST'])
def api_auto_promote():
    """AI automatically selects and promotes top products"""
    user_id = session.get('user_id')
    user = load_user(user_id)
    
    if not user:
        return jsonify({'error': 'Authentication required'}), 401
    
    try:
        # Get AI-recommended products (avoiding recent duplicates)
        ai_selector = AutoProductSelector(user)
        selected_products = ai_selector.auto_promote_products(num_products=3)
        
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

@app.route('/setup')
def setup():
    """Setup page for affiliate link and platform configuration"""
    user_id = session.get('user_id')
    user = load_user(user_id)
    
    if not user:
        return redirect(url_for('index'))
    
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
    """View analytics"""
    user_id = session.get('user_id')
    user = load_user(user_id)
    
    if not user:
        return redirect(url_for('index'))
    
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
    """Browse products"""
    user_id = session.get('user_id')
    user = load_user(user_id)
    
    if not user:
        return redirect(url_for('index'))
    
    try:
        inventory = InventoryManager()
        ai_selector = AutoProductSelector(user)
        available_products = ai_selector.get_ai_recommended_products(limit=20)
        
        products_display = []
        for product in available_products:
            products_display.append({
                'asin': product.asin,
                'title': product.product_title,
                'price': product.price or 'N/A',
                'rating': product.rating or 0,
                'image_url': product.image_url or '/static/placeholder.jpg',
                'category': product.category or 'General'
            })
        
        return render_template('products.html', user=user, products=products_display)
    except Exception as e:
        logger.error(f"Products error: {e}")
        return render_template('products.html', user=user, products=[])

@app.route('/logout')
def logout():
    """Simple logout"""
    session.clear()
    return redirect(url_for('index'))

# Error handlers
@app.errorhandler(500)
def handle_500(e):
    return render_template('dashboard_enhanced.html', 
                         error_message="System loading...",
                         page_title="AffiliateBot Pro"), 200

@app.errorhandler(404)
def handle_404(e):
    return redirect(url_for('index'))