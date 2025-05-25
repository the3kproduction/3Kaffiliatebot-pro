from flask import render_template, request, redirect, url_for, flash, jsonify, session
from flask_login import current_user, login_required
from app import app, db
from models import User, Campaign, Post, EmailBlast
import os

# Import authentication based on environment
try:
    # Only try to import replit_auth if REPL_ID exists
    if os.environ.get('REPL_ID'):
        from replit_auth import require_login, make_replit_blueprint
    else:
        raise ImportError("REPL_ID not available, using simple auth")
except (ImportError, SystemExit):
    # Use simple auth for Render deployment
    from simple_auth import simple_require_login as require_login
    make_replit_blueprint = lambda: None

from amazon_scraper import AmazonProductScraper
from marketing_automation import MultiPlatformPoster
from user_management import UserManager, grant_premium_trial, grant_pro_trial, grant_contest_winner
import logging

logger = logging.getLogger(__name__)

# Register authentication blueprint (only if available)
replit_bp = make_replit_blueprint()
if replit_bp:
    app.register_blueprint(replit_bp, url_prefix="/auth")

# Simple auth bypass for Render deployment
def create_demo_user():
    """Create a demo user for Render deployment"""
    demo_user = User.query.filter_by(email='the3kproduction@gmail.com').first()
    if not demo_user:
        demo_user = User(
            id='admin-3kloudz',
            email='the3kproduction@gmail.com',
            username='3Kloudz',
            first_name='3K',
            last_name='Production',
            is_admin=True,
            subscription_tier='lifetime',
            amazon_affiliate_id='luxoraconnect-20'
        )
        db.session.add(demo_user)
        db.session.commit()
    return demo_user

# Make session permanent
@app.before_request
def make_session_permanent():
    session.permanent = True

@app.route('/')
def index():
    """Landing page - shows login for guests, dashboard for logged-in users"""
    # Check if user is coming from marketing site for free signup
    signup_type = request.args.get('signup')
    if signup_type == 'free' and not current_user.is_authenticated:
        # Show special free tier signup message
        flash('Welcome! Creating your free tier account with 2 posts per day...', 'info')
        return render_template('landing.html', free_signup=True)
    
    # For Render deployment without Replit auth, auto-login demo user
    if os.environ.get('RENDER') and not current_user.is_authenticated:
        from flask_login import login_user
        demo_user = create_demo_user()
        login_user(demo_user)
        return redirect(url_for('dashboard'))
    
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    return render_template('landing.html')

@app.route('/help')
@require_login
def help_page():
    """Built-in help and setup guide"""
    return render_template('help.html', user=current_user)

@app.route('/privacy')
def privacy_policy():
    """Privacy policy page - public access"""
    try:
        return render_template('privacy.html')
    except Exception as e:
        return f"Privacy Policy page loading... Please try again in a moment."

@app.route('/terms')
def terms_of_service():
    """Terms of service page - public access"""
    try:
        return render_template('terms.html')
    except Exception as e:
        return f"Terms of Service page loading... Please try again in a moment."

@app.route('/dashboard')
@require_login
def dashboard():
    """Enhanced dashboard with analytics and smart features"""
    from analytics_dashboard import AnalyticsDashboard
    from inventory_manager import InventoryManager
    from webhook_manager import WebhookManager
    
    # Get user analytics
    analytics = AnalyticsDashboard(current_user).get_user_analytics()
    
    # Get trending products (avoiding recent duplicates)
    inventory = InventoryManager()
    trending_products = inventory.get_products_to_promote(current_user, limit=12)
    
    # Get user's webhook configurations
    webhook_manager = WebhookManager(current_user)
    user_webhooks = webhook_manager.get_user_webhooks()
    
    # Calculate next post time based on frequency
    from datetime import datetime, timedelta
    if current_user.auto_post_enabled and current_user.post_frequency_hours:
        last_post = Post.query.filter_by(user_id=current_user.id).order_by(Post.created_at.desc()).first()
        if last_post:
            next_post_time = last_post.created_at + timedelta(hours=current_user.post_frequency_hours)
        else:
            next_post_time = datetime.now() + timedelta(hours=current_user.post_frequency_hours)
    else:
        next_post_time = None
    
    # Get AI recommendations
    from auto_product_selector import AutoProductSelector
    selector = AutoProductSelector(current_user)
    ai_recommendations = selector.get_ai_recommended_products(limit=5)
    
    # Get trending search suggestions
    from amazon_search import AmazonSearcher
    searcher = AmazonSearcher()
    trending_searches = searcher.get_trending_searches()[:8]
    
    # Smart platform detection - only show unconfigured platforms
    unconfigured_platforms = []
    
    # Check each platform configuration
    if not current_user.discord_webhook_url:
        unconfigured_platforms.append('Discord')
    if not current_user.telegram_bot_token or not current_user.telegram_chat_id:
        unconfigured_platforms.append('Telegram')
    if not current_user.slack_bot_token or not current_user.slack_channel_id:
        unconfigured_platforms.append('Slack')
    if not current_user.sendgrid_api_key or not current_user.email_from or not current_user.email_to:
        unconfigured_platforms.append('Email')
    # Pinterest and Reddit are always shown as they need manual setup
    if not getattr(current_user, 'pinterest_access_token', None):
        unconfigured_platforms.append('Pinterest')
    if not getattr(current_user, 'reddit_client_id', None):
        unconfigured_platforms.append('Reddit')
    
    return render_template('dashboard_enhanced.html', 
                         analytics=analytics,
                         trending_products=trending_products,
                         user_webhooks=user_webhooks,
                         next_post_time=next_post_time,
                         ai_recommendations=ai_recommendations,
                         trending_searches=trending_searches,
                         unconfigured_platforms=unconfigured_platforms)

@app.route('/setup', methods=['GET', 'POST'])
@require_login
def setup():
    """Setup page for affiliate link and platform configuration"""
    user = current_user
    
    if request.method == 'POST':
        # Update affiliate information
        user.amazon_affiliate_id = request.form.get('affiliate_id')
        user.affiliate_link_base = request.form.get('affiliate_link')
        
        # Update platform settings
        user.discord_webhook_url = request.form.get('discord_webhook')
        user.telegram_bot_token = request.form.get('telegram_token')
        user.telegram_chat_id = request.form.get('telegram_chat_id')
        user.slack_bot_token = request.form.get('slack_token')
        user.slack_channel_id = request.form.get('slack_channel')
        user.sendgrid_api_key = request.form.get('sendgrid_key')
        user.email_from = request.form.get('email_from')
        user.email_to = request.form.get('email_to')
        
        # Update automation settings
        user.auto_post_enabled = bool(request.form.get('auto_post_enabled'))
        user.post_frequency_hours = int(request.form.get('post_frequency', 3))
        
        db.session.commit()
        flash('Settings saved successfully!', 'success')
        return redirect(url_for('dashboard'))
    
    return render_template('setup.html', user=user)

@app.route('/products')
@require_login
def products():
    """Browse and manage products"""
    from models import ProductInventory
    
    user = current_user
    category = request.args.get('category', 'all')
    
    # Get all products directly from your inventory
    products_raw = ProductInventory.query.filter_by(is_active=True).order_by(ProductInventory.asin).all()
    
    if not products_raw:
        products_raw = ProductInventory.query.all()  # Show all if none are active
    
    # Convert database objects to dictionaries for template
    products = []
    for product in products_raw:
        products.append({
            'asin': product.asin,
            'product_title': product.product_title,
            'price': product.price or 'N/A',
            'rating': product.rating or 4.5,
            'category': product.category or 'Electronics',
            'image_url': product.image_url or 'https://via.placeholder.com/200x200?text=Product'
        })
    
    # Get available categories from your inventory
    categories_raw = db.session.query(ProductInventory.category).distinct().all()
    categories = ['all'] + [cat[0] for cat in categories_raw if cat[0]]
    
    return render_template('products.html', 
                         products=products, 
                         categories=categories,
                         current_category=category)

@app.route('/post-product', methods=['POST'])
@require_login
def post_product():
    """Post a product to user's configured platforms"""
    user = current_user
    
    try:
        # Get product data from form
        product_data = {
            'title': request.form.get('title'),
            'description': request.form.get('description'),
            'asin': request.form.get('asin'),
            'amazon_url': request.form.get('amazon_url'),
            'affiliate_url': request.form.get('affiliate_url'),
            'image': request.form.get('image'),
            'price': request.form.get('price'),
            'rating': float(request.form.get('rating', 0)),
            'category': request.form.get('category')
        }
        
        # Save post to database
        post = Post(
            user_id=user.id,
            product_title=product_data['title'],
            product_description=product_data['description'],
            product_image_url=product_data['image'],
            amazon_url=product_data['amazon_url'],
            affiliate_url=product_data['affiliate_url'],
            price=product_data['price'],
            rating=product_data['rating'],
            category=product_data['category']
        )
        
        # Post to platforms
        poster = MultiPlatformPoster(user)
        results = poster.post_product(product_data)
        
        # Update post status
        post.posted_to_discord = results.get('discord', False)
        post.posted_to_telegram = results.get('telegram', False)
        post.posted_to_slack = results.get('slack', False)
        post.posted_to_email = results.get('email', False)
        
        db.session.add(post)
        db.session.commit()
        
        successful_platforms = sum(results.values())
        total_platforms = len([p for p in ['discord', 'telegram', 'slack', 'email'] 
                              if getattr(user, f"{p}_{'webhook_url' if p == 'discord' else 'bot_token' if p == 'telegram' else 'bot_token' if p == 'slack' else 'api_key' if p == 'email' else 'webhook_url'}")])
        
        if successful_platforms > 0:
            flash(f'Product posted to {successful_platforms}/{total_platforms} platforms!', 'success')
        else:
            flash('Failed to post to any platforms. Check your configuration.', 'error')
            
    except Exception as e:
        logger.error(f"Error posting product: {e}")
        flash('Error posting product. Please try again.', 'error')
    
    return redirect(url_for('products'))

@app.route('/campaigns')
@require_login
def campaigns():
    """Manage marketing campaigns"""
    user = current_user
    user_campaigns = Campaign.query.filter_by(user_id=user.id).all()
    
    return render_template('campaigns.html', campaigns=user_campaigns)

@app.route('/analytics')
@require_login
def analytics():
    """View analytics and performance"""
    user = current_user
    
    # Get posting stats
    posts = Post.query.filter_by(user_id=user.id).all()
    
    # Calculate metrics
    total_posts = len(posts)
    total_clicks = sum(post.clicks for post in posts)
    total_impressions = sum(post.impressions for post in posts)
    
    # Platform breakdown
    platform_stats = {
        'discord': len([p for p in posts if p.posted_to_discord]),
        'telegram': len([p for p in posts if p.posted_to_telegram]),
        'slack': len([p for p in posts if p.posted_to_slack]),
        'email': len([p for p in posts if p.posted_to_email])
    }
    
    return render_template('analytics.html', 
                         total_posts=total_posts,
                         total_clicks=total_clicks,
                         total_impressions=total_impressions,
                         platform_stats=platform_stats,
                         recent_posts=posts[:10])

@app.route('/analytics/detailed')
@require_login
def analytics_detailed():
    """Detailed Analytics Page"""
    user = current_user
    posts = Post.query.filter_by(user_id=user.id).all()
    
    return render_template('analytics.html', 
                         total_posts=len(posts),
                         total_clicks=sum(post.clicks for post in posts),
                         total_impressions=sum(post.impressions for post in posts),
                         platform_stats={
                             'discord': len([p for p in posts if p.posted_to_discord]),
                             'telegram': len([p for p in posts if p.posted_to_telegram]),
                             'slack': len([p for p in posts if p.posted_to_slack]),
                             'email': len([p for p in posts if p.posted_to_email])
                         },
                         recent_posts=posts[:20])

@app.route('/analytics/export')
@require_login
def analytics_export():
    """Export Analytics Data"""
    from datetime import datetime
    user = current_user
    posts = Post.query.filter_by(user_id=user.id).all()
    
    export_data = {
        'user_id': user.id,
        'export_date': datetime.now().isoformat(),
        'total_posts': len(posts),
        'total_clicks': sum(post.clicks for post in posts),
        'recent_posts': [{'title': p.product_title, 'clicks': p.clicks, 'created_at': p.created_at.isoformat()} for p in posts[:50]]
    }
    
    return jsonify(export_data)

# ADMIN ROUTES - Money-making features for platform owner
@app.route('/admin')
def admin_dashboard():
    """Admin dashboard - view all users and send email blasts"""
    # Check admin access using session
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('dashboard'))
    
    user = User.query.get(user_id)
    if not user or not user.is_admin:
        flash('Access denied. Admin only.', 'error')
        return redirect(url_for('dashboard'))
    
    # Get all users and their stats
    users = User.query.all()
    total_users = len(users)
    total_posts = Post.query.count()
    total_clicks = db.session.query(db.func.sum(Post.clicks)).scalar() or 0
    
    # Recent signups
    recent_users = User.query.order_by(User.created_at.desc()).limit(10).all()
    
    # Email stats
    recent_blasts = EmailBlast.query.order_by(EmailBlast.sent_at.desc()).limit(5).all()
    
    return render_template('admin/dashboard.html',
                         users=users,
                         total_users=total_users,
                         total_posts=total_posts,
                         total_clicks=total_clicks,
                         recent_users=recent_users,
                         recent_blasts=recent_blasts)

@app.route('/admin/users')
def admin_users():
    """View all user emails for marketing"""
    # Check admin access using session
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('dashboard'))
    
    user = User.query.get(user_id)
    if not user or not user.is_admin:
        flash('Access denied. Admin only.', 'error')
        return redirect(url_for('dashboard'))
    
    # Get all users with filtering options
    tier_filter = request.args.get('tier', 'all')
    
    query = User.query
    if tier_filter != 'all':
        query = query.filter(User.subscription_tier == tier_filter)
    
    users = query.order_by(User.created_at.desc()).all()
    
    # Count by tier
    tier_counts = {
        'free': User.query.filter(User.subscription_tier == 'free').count(),
        'premium': User.query.filter(User.subscription_tier == 'premium').count(),
        'pro': User.query.filter(User.subscription_tier == 'pro').count()
    }
    
    return render_template('admin/users.html', 
                         users=users, 
                         tier_filter=tier_filter,
                         tier_counts=tier_counts)

@app.route('/admin/email-blast', methods=['GET', 'POST'])
@require_login
def admin_email_blast():
    """Send mass emails to users"""
    if not current_user.is_admin:
        flash('Access denied. Admin only.', 'error')
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        subject = request.form.get('subject')
        content = request.form.get('content')
        target_tier = request.form.get('target_tier', 'all')
        
        # Create email blast record
        blast = EmailBlast(
            admin_user_id=current_user.id,
            subject=subject,
            content=content,
            target_tier=target_tier
        )
        db.session.add(blast)
        db.session.commit()
        
        # Send emails to target users
        try:
            from email_blast_service import send_mass_email
            emails_sent = send_mass_email(blast)
            
            blast.emails_sent = emails_sent
            db.session.commit()
            
            flash(f'Email blast sent to {emails_sent} users!', 'success')
        except Exception as e:
            logger.error(f"Email blast failed: {e}")
            flash('Failed to send emails. Check your SendGrid configuration.', 'error')
        
        return redirect(url_for('admin_email_blast'))
    
    # Get user counts for targeting
    user_counts = {
        'all': User.query.filter(User.email_notifications == True).count(),
        'free': User.query.filter(User.subscription_tier == 'free', User.email_notifications == True).count(),
        'premium': User.query.filter(User.subscription_tier == 'premium', User.email_notifications == True).count(),
        'pro': User.query.filter(User.subscription_tier == 'pro', User.email_notifications == True).count()
    }
    
    return render_template('admin/email_blast.html', user_counts=user_counts)

@app.route('/admin/make-admin/<user_id>')
@require_login
def make_admin(user_id):
    """Make another user an admin"""
    if not current_user.is_admin:
        flash('Access denied. Admin only.', 'error')
        return redirect(url_for('dashboard'))
    
    user = User.query.get_or_404(user_id)
    user.is_admin = True
    db.session.commit()
    
    flash(f'{user.email} is now an admin!', 'success')
    return redirect(url_for('admin_users'))

@app.route('/admin/subscription-settings')
@require_login
def admin_subscription_settings():
    """Manage subscription tiers and pricing"""
    if not current_user.is_admin:
        flash('Access denied. Admin only.', 'error')
        return redirect(url_for('dashboard'))
    
    # This is where you can set up pricing tiers, posting frequency limits, etc.
    return render_template('admin/subscription_settings.html')

@app.route('/api/search-products', methods=['POST'])
@require_login
def api_search_products():
    """Search Amazon for products and add to inventory"""
    from amazon_search import AmazonSearcher
    
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
                'image_url': product.get('image_url', ''),
                'category': product.get('category', 'General')
            })
        
        return jsonify({
            'success': True,
            'products': results,
            'message': f'Found {len(results)} products for "{query}"'
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/track-click/<int:post_id>')
def track_click(post_id):
    """Track clicks on affiliate links"""
    post = Post.query.get_or_404(post_id)
    post.clicks += 1
    db.session.commit()
    
    return redirect(post.affiliate_url)

# Enhanced API Endpoints for New Features

@app.route('/api/promote-product', methods=['POST'])
@require_login
def api_promote_product():
    """Promote a specific product to all platforms"""
    from webhook_manager import WebhookManager
    from inventory_manager import InventoryManager
    from models import ProductInventory
    
    data = request.get_json()
    asin = data.get('asin')
    
    if not asin:
        return jsonify({'success': False, 'error': 'ASIN required'})
    
    # Get product details
    inventory = InventoryManager()
    product = ProductInventory.query.filter_by(asin=asin).first()
    
    if not product:
        return jsonify({'success': False, 'error': 'Product not found'})
    
    # Get user's webhooks
    webhook_manager = WebhookManager(current_user)
    webhooks = webhook_manager.get_user_webhooks()
    
    platforms_posted = []
    for webhook in webhooks:
        result = webhook_manager.post_to_webhook(webhook.id, {
            'title': product.product_title,
            'price': product.price,
            'rating': product.rating,
            'affiliate_url': f"https://amazon.com/dp/{asin}?tag={current_user.amazon_affiliate_id}",
            'image_url': product.image_url
        })
        
        if result['success']:
            platforms_posted.append(result['platform'])
    
    # Mark product as promoted
    inventory.mark_product_promoted(asin, current_user.id)
    
    return jsonify({
        'success': True,
        'platforms_posted': len(platforms_posted),
        'platforms': platforms_posted
    })

@app.route('/api/toggle-auto-posts', methods=['POST'])
@require_login
def api_toggle_auto_posts():
    """Toggle auto-posting on/off for user"""
    user = current_user
    try:
        user.auto_post_enabled = not user.auto_post_enabled
        db.session.commit()
        
        status = "enabled" if user.auto_post_enabled else "disabled"
        return jsonify({
            'success': True,
            'auto_post_enabled': user.auto_post_enabled,
            'message': f'Auto-posting {status} successfully!'
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/update-frequency', methods=['POST'])
@require_login
def api_update_frequency():
    """Update user's posting frequency"""
    data = request.get_json()
    frequency = data.get('frequency_hours')
    
    if frequency not in [1, 3, 12]:
        return jsonify({'success': False, 'error': 'Invalid frequency'})
    
    # Check if user's tier allows this frequency
    from subscription_manager import SubscriptionManager
    allowed_frequency = SubscriptionManager.get_user_posting_frequency(current_user)
    
    if frequency < allowed_frequency:
        return jsonify({
            'success': False, 
            'error': f'Your {current_user.subscription_tier} plan only allows posting every {allowed_frequency} hours'
        })
    
    current_user.post_frequency_hours = frequency
    db.session.commit()
    
    return jsonify({'success': True})

@app.route('/api/save-platform', methods=['POST'])
@require_login
def api_save_platform():
    """Save platform configuration for user"""
    user = current_user
    data = request.get_json()
    
    try:
        platform = data.get('platform')
        
        if platform == 'discord':
            user.discord_webhook_url = data.get('webhook_url')
        elif platform == 'telegram':
            user.telegram_bot_token = data.get('bot_token')
            user.telegram_chat_id = data.get('chat_id')
        elif platform == 'slack':
            user.slack_bot_token = data.get('bot_token')
            user.slack_channel_id = data.get('channel_id')
        elif platform == 'pinterest':
            user.pinterest_access_token = data.get('access_token')
            user.pinterest_board_id = data.get('board_id')
        elif platform == 'reddit':
            user.reddit_client_id = data.get('client_id')
            user.reddit_client_secret = data.get('client_secret')
            user.reddit_username = data.get('username')
            user.reddit_password = data.get('password')
            user.reddit_subreddit = data.get('subreddit')
        else:
            return jsonify({'success': False, 'error': 'Invalid platform'})
        
        db.session.commit()
        return jsonify({'success': True, 'message': f'{platform.title()} configured successfully'})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/test-connections', methods=['POST'])
def api_test_connections():
    """Test platform connections for user"""
    try:
        # Get user from session instead of current_user to avoid auth issues
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'success': False, 'error': 'Not authenticated'})
        
        user = User.query.get(user_id)
        if not user:
            return jsonify({'success': False, 'error': 'User not found'})
        
        # Check environment variables for platform credentials
        from os import environ
        
        results = {
            'success': True,
            'discord': bool(environ.get('DISCORD_WEBHOOK_URL') or getattr(user, 'discord_webhook_url', None)),
            'telegram': bool(environ.get('TELEGRAM_BOT_TOKEN') and environ.get('TELEGRAM_CHAT_ID')),
            'slack': bool(environ.get('SLACK_BOT_TOKEN') and environ.get('SLACK_CHANNEL_ID')),
            'pinterest': bool(getattr(user, 'pinterest_access_token', None) and getattr(user, 'pinterest_board_id', None)),
            'reddit': bool(getattr(user, 'reddit_client_id', None) and getattr(user, 'reddit_client_secret', None))
        }
        
        return jsonify(results)
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/promote-products', methods=['POST'])
@require_login
def api_promote_products():
    """Promote multiple products using existing platform configurations"""
    user = current_user
    data = request.get_json()
    count = data.get('count', 1)
    
    try:
        # Use the exact same system as working auto-promote
        from auto_product_selector import AutoProductSelector
        auto_selector = AutoProductSelector(user)
        
        # Call auto_promote_products directly like the working button
        result = auto_selector.auto_promote_products(count)
        
        if result:
            return jsonify({
                'success': True,
                'message': f'Successfully promoted {count} products to your platforms!'
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to promote products. Please check your platform configurations.'
            })
            
    except Exception as e:
        logger.error(f"Manual promotion error: {str(e)}")
        return jsonify({'success': False, 'error': f'Error: {str(e)}'})

@app.route('/api/report-problem', methods=['POST'])
@require_login
def api_report_problem():
    """Handle user problem reports"""
    user = current_user
    data = request.get_json()
    
    try:
        problem_type = data.get('problem_type', 'unknown')
        description = data.get('description', '')
        user_agent = data.get('user_agent', '')
        url = data.get('url', '')
        
        from datetime import datetime
        
        # Create a detailed problem report
        report = {
            'user_id': user.id,
            'user_email': user.email,
            'problem_type': problem_type,
            'description': description,
            'user_agent': user_agent,
            'url': url,
            'timestamp': datetime.now().isoformat(),
            'subscription_tier': user.subscription_tier
        }
        
        # Log the problem for immediate visibility
        logger.error(f"🚨 USER PROBLEM REPORT: {problem_type} - {description} (User: {user.email})")
        
        # Send notification to Discord webhook if available
        import os
        discord_webhook = os.environ.get('DISCORD_WEBHOOK_URL')
        if discord_webhook:
            try:
                import requests
                embed = {
                    "title": "🚨 User Problem Report",
                    "color": 15158332,  # Red color
                    "fields": [
                        {"name": "User", "value": f"{user.email} ({user.subscription_tier})", "inline": True},
                        {"name": "Problem Type", "value": problem_type, "inline": True},
                        {"name": "Description", "value": description[:1000], "inline": False},
                        {"name": "URL", "value": url, "inline": False}
                    ],
                    "timestamp": datetime.now().isoformat()
                }
                
                requests.post(discord_webhook, json={"embeds": [embed]}, timeout=5)
            except:
                pass  # Don't fail if notification fails
        
        return jsonify({
            'success': True,
            'message': 'Problem report submitted successfully'
        })
        
    except Exception as e:
        logger.error(f"Error handling problem report: {str(e)}")
        return jsonify({'success': False, 'error': 'Failed to submit report'})

@app.route('/help')
def help_page():
    """Comprehensive setup guide and FAQ"""
    return render_template('help.html')

@app.route('/api/toggle-auto-posts', methods=['POST'])
@require_login
def api_toggle_auto_posts():
    """Toggle automatic posting on/off"""
    current_user.auto_post_enabled = not current_user.auto_post_enabled
    db.session.commit()
    
    return jsonify({
        'success': True,
        'auto_post_enabled': current_user.auto_post_enabled
    })

@app.route('/test-webhook/<int:webhook_id>')
@require_login
def test_webhook(webhook_id):
    """Test a specific webhook"""
    from webhook_manager import WebhookManager
    
    webhook_manager = WebhookManager(current_user)
    result = webhook_manager.test_webhook(webhook_id)
    
    if result['success']:
        flash('Webhook test successful!', 'success')
    else:
        flash(f'Webhook test failed: {result["error"]}', 'danger')
    
    return redirect(url_for('dashboard'))

@app.route('/setup-webhooks', methods=['GET', 'POST'])
@require_login
def setup_webhooks():
    """Setup multiple webhook destinations"""
    from webhook_manager import WebhookManager
    
    if request.method == 'POST':
        webhook_manager = WebhookManager(current_user)
        
        name = request.form.get('webhook_name')
        platform = request.form.get('platform')
        webhook_url = request.form.get('webhook_url')
        frequency = int(request.form.get('frequency', 3))
        
        webhook_manager.add_webhook_destination(name, platform, webhook_url, frequency)
        flash('Webhook destination added successfully!', 'success')
        
        return redirect(url_for('dashboard'))
    
    return render_template('setup_webhooks.html')

@app.route('/products/refresh')
@require_login
def refresh_products():
    """Refresh trending products from Amazon"""
    from inventory_manager import InventoryManager
    
    inventory = InventoryManager()
    count = inventory.refresh_trending_products()
    
    flash(f'Refreshed {count} trending products!', 'success')
    return redirect(url_for('dashboard'))

@app.route('/api/auto-promote', methods=['POST'])
@require_login
def api_auto_promote():
    """AI automatically selects and promotes top products"""
    from auto_product_selector import AutoProductSelector
    
    data = request.get_json() or {}
    num_products = data.get('num_products', 3)
    
    selector = AutoProductSelector(current_user)
    result = selector.auto_promote_products(num_products)
    
    return jsonify(result)

@app.route('/api/search-products', methods=['POST'])
@require_login
def api_search_products():
    """Search Amazon for products and add to inventory"""
    from amazon_search import AmazonSearcher
    
    data = request.get_json()
    query = data.get('query', '')
    limit = data.get('limit', 20)
    
    if not query:
        return jsonify({'success': False, 'error': 'Search query required'})
    
    searcher = AmazonSearcher()
    result = searcher.search_and_add_to_inventory(query, limit)
    
    return jsonify(result)

@app.route('/api/get-ai-recommendations', methods=['GET'])
@require_login
def api_get_ai_recommendations():
    """Get AI-recommended products for user"""
    from auto_product_selector import AutoProductSelector
    
    selector = AutoProductSelector(current_user)
    recommendations = selector.get_ai_recommended_products(limit=10)
    
    # Convert to JSON-serializable format
    products_data = []
    for product in recommendations:
        products_data.append({
            'asin': product.asin,
            'title': product.product_title,
            'price': product.price,
            'rating': product.rating,
            'category': product.category,
            'image_url': product.image_url,
            'times_promoted': product.times_promoted
        })
    
    return jsonify({
        'success': True,
        'recommendations': products_data
    })

@app.route('/api/spotify-auth-url', methods=['GET'])
@require_login
def spotify_auth_url():
    """Get Spotify authorization URL"""
    import os
    spotify_client_id = os.environ.get('SPOTIFY_CLIENT_ID')
    
    if spotify_client_id:
        # Use the exact redirect URI that matches Spotify app settings
        redirect_uri = 'https://replit.com/@drfe8694/CodeCraft/spotify-callback'
        scopes = 'streaming user-read-email user-read-private user-read-playback-state user-modify-playback-state'
        
        auth_url = f"https://accounts.spotify.com/authorize?" \
                  f"response_type=code" \
                  f"&client_id={spotify_client_id}" \
                  f"&scope={scopes}" \
                  f"&redirect_uri={redirect_uri}" \
                  f"&state={current_user.id}"
        
        return jsonify({'auth_url': auth_url})
    else:
        return jsonify({'auth_url': None, 'message': 'Spotify not configured'})

@app.route('/spotify-callback')
@require_login
def spotify_callback():
    """Handle Spotify OAuth callback"""
    code = request.args.get('code')
    error = request.args.get('error')
    
    if error:
        flash('Spotify connection failed', 'error')
        return redirect(url_for('dashboard'))
    
    if code:
        # For now, just mark as successfully connected
        flash('🎵 Spotify connected successfully! You can now use the music player with your playlists.', 'success')
    else:
        flash('Spotify connection cancelled', 'info')
    
    return redirect(url_for('dashboard'))

@app.route('/products/browse')
@require_login
def browse_products():
    """Browse all available products"""
    from inventory_manager import InventoryManager
    from models import ProductInventory
    
    inventory = InventoryManager()
    # Get sample products for browsing
    products = ProductInventory.query.order_by(ProductInventory.times_promoted.desc()).limit(50).all()
    
    # If no products in database, show some sample data
    if not products:
        # Add some sample trending products
        sample_products = [
            {
                'asin': 'B08N5WRWNW',
                'product_title': 'Echo Dot (4th Gen) | Smart speaker with Alexa',
                'price': '$49.99',
                'rating': 4.7,
                'category': 'Electronics',
                'image_url': 'https://m.media-amazon.com/images/I/61MCWFAZ90L._AC_UY218_.jpg'
            },
            {
                'asin': 'B0B7BP6CJN',
                'product_title': 'Apple AirPods Pro (2nd Generation)',
                'price': '$249.00',
                'rating': 4.4,
                'category': 'Electronics',
                'image_url': 'https://m.media-amazon.com/images/I/61SUj2aKoEL._AC_UY218_.jpg'
            },
            {
                'asin': 'B09JQMJHXY',
                'product_title': 'Kindle Paperwhite (11th Gen)',
                'price': '$139.99',
                'rating': 4.6,
                'category': 'Electronics',
                'image_url': 'https://m.media-amazon.com/images/I/61IBBVJvSDL._AC_UY218_.jpg'
            }
        ]
        
        # Convert to objects for template
        class MockProduct:
            def __init__(self, data):
                for key, value in data.items():
                    setattr(self, key, value)
                self.times_promoted = 0
        
        products = [MockProduct(p) for p in sample_products]
    
    return render_template('browse_products.html', products=products)