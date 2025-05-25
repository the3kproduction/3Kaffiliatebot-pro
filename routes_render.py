"""
Render-specific routes that bypass Replit authentication
"""
from flask import render_template, request, redirect, url_for, flash, jsonify, session
from flask_login import current_user, login_required, login_user
from run_render import app, db
from models import User, Campaign, Post, EmailBlast
from simple_auth import simple_require_login, create_demo_user
from amazon_scraper import AmazonProductScraper
from marketing_automation import MultiPlatformPoster
import logging
import os

logger = logging.getLogger(__name__)

# Use simple authentication for all routes
require_login = simple_require_login

# Make session permanent
@app.before_request
def make_session_permanent():
    session.permanent = True

@app.route('/')
def index():
    """Landing page - auto-login demo user for Render"""
    if not current_user.is_authenticated:
        demo_user = create_demo_user()
        login_user(demo_user)
        return redirect(url_for('dashboard'))
    
    return redirect(url_for('dashboard'))

@app.route('/dashboard')
@require_login
def dashboard():
    """Enhanced dashboard with analytics and smart features"""
    from analytics_dashboard import AnalyticsDashboard
    from auto_product_selector import AutoProductSelector
    from inventory_manager import InventoryManager
    
    # Get user analytics
    analytics = AnalyticsDashboard(current_user)
    user_stats = analytics.get_user_analytics(days=30)
    
    # Get AI recommendations
    ai_selector = AutoProductSelector(current_user)
    ai_recommendations = ai_selector.get_ai_recommended_products(limit=6)
    
    # Get available products for promotion
    inventory = InventoryManager()
    available_products = inventory.get_products_to_promote(current_user, limit=12)
    
    # Recent posts
    recent_posts = Post.query.filter_by(user_id=current_user.id).order_by(Post.created_at.desc()).limit(5).all()
    
    return render_template('dashboard_enhanced.html',
                         user=current_user,
                         stats=user_stats,
                         ai_recommendations=ai_recommendations,
                         available_products=available_products,
                         recent_posts=recent_posts)

@app.route('/setup')
@require_login
def setup():
    """Setup page for affiliate link and platform configuration"""
    return render_template('setup.html', user=current_user)

@app.route('/setup', methods=['POST'])
@require_login
def setup_post():
    """Handle setup form submission"""
    # Update user configuration
    current_user.amazon_affiliate_id = request.form.get('affiliate_id')
    current_user.affiliate_link_base = request.form.get('affiliate_link_base')
    
    # Platform configurations
    current_user.discord_webhook_url = request.form.get('discord_webhook')
    current_user.telegram_bot_token = request.form.get('telegram_token')
    current_user.telegram_chat_id = request.form.get('telegram_chat_id')
    current_user.slack_bot_token = request.form.get('slack_token')
    current_user.slack_channel_id = request.form.get('slack_channel')
    current_user.sendgrid_api_key = request.form.get('sendgrid_key')
    current_user.email_from = request.form.get('email_from')
    current_user.email_to = request.form.get('email_to')
    
    # Automation settings
    current_user.auto_post_enabled = 'auto_post' in request.form
    frequency = request.form.get('frequency', 3)
    current_user.post_frequency_hours = int(frequency) if frequency.isdigit() else 3
    
    db.session.commit()
    flash('Configuration saved successfully!', 'success')
    return redirect(url_for('dashboard'))

@app.route('/products')
@require_login
def products():
    """Browse and manage products"""
    from inventory_manager import InventoryManager
    
    inventory = InventoryManager()
    available_products = inventory.get_products_to_promote(current_user, limit=50)
    
    return render_template('products.html', 
                         products=available_products,
                         user=current_user)

@app.route('/analytics')
@require_login
def analytics():
    """View analytics and performance"""
    from analytics_dashboard import AnalyticsDashboard
    
    analytics_dashboard = AnalyticsDashboard(current_user)
    stats = analytics_dashboard.get_user_analytics(days=30)
    product_performance = analytics_dashboard.get_product_performance(limit=20)
    
    return render_template('analytics.html',
                         stats=stats,
                         product_performance=product_performance,
                         user=current_user)

# Add all other routes here without Replit auth dependencies...
# For brevity, I'll add the key API routes

@app.route('/api/search-products', methods=['POST'])
@require_login
def api_search_products():
    """Search Amazon for products and add to inventory"""
    query = request.json.get('query', '')
    if not query:
        return jsonify({'error': 'Search query required'}), 400
    
    try:
        from amazon_search import AmazonSearcher
        searcher = AmazonSearcher()
        results = searcher.search_and_add_to_inventory(query, limit=20)
        
        return jsonify({
            'success': True,
            'products_found': len(results),
            'products': results
        })
    except Exception as e:
        logger.error(f"Search error: {e}")
        return jsonify({'error': 'Search failed'}), 500

@app.route('/api/auto-promote', methods=['POST'])
@require_login
def api_auto_promote():
    """AI automatically selects and promotes top products"""
    try:
        from auto_product_selector import AutoProductSelector
        
        ai_selector = AutoProductSelector(current_user)
        promoted_products = ai_selector.auto_promote_products(num_products=3)
        
        return jsonify({
            'success': True,
            'promoted_count': len(promoted_products),
            'products': [p.product_title for p in promoted_products]
        })
    except Exception as e:
        logger.error(f"Auto-promote error: {e}")
        return jsonify({'error': 'Auto-promotion failed'}), 500

# Simple logout route
@app.route('/logout')
def logout():
    """Simple logout - redirect to home"""
    from flask_login import logout_user
    logout_user()
    return redirect(url_for('index'))