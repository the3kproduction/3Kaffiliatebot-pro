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
        
        # Convert to display format
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
        
        return render_template('dashboard_enhanced.html',
                             user=user,
                             campaigns=campaigns,
                             recent_posts=recent_posts,
                             total_posts=total_posts,
                             total_clicks=total_clicks,
                             recommended_products=products_display,
                             page_title="AffiliateBot Pro Dashboard")
    
    except Exception as e:
        logger.error(f"Dashboard error: {e}")
        return render_template('dashboard_enhanced.html',
                             user=user,
                             campaigns=[],
                             recent_posts=[],
                             total_posts=0,
                             total_clicks=0,
                             recommended_products=[],
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