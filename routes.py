from flask import render_template, request, redirect, url_for, flash, jsonify, session
from flask_login import current_user, login_required
from app import app, db
from models import User, Campaign, Post, EmailBlast
from replit_auth import require_login, make_replit_blueprint
from amazon_scraper import AmazonProductScraper
from marketing_automation import MultiPlatformPoster
import logging

logger = logging.getLogger(__name__)

# Register authentication blueprint
app.register_blueprint(make_replit_blueprint(), url_prefix="/auth")

# Make session permanent
@app.before_request
def make_session_permanent():
    session.permanent = True

@app.route('/')
def index():
    """Landing page - shows login for guests, dashboard for logged-in users"""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    return render_template('landing.html')

@app.route('/dashboard')
@require_login
def dashboard():
    """Main dashboard for logged-in users"""
    user = current_user
    
    # Get user's recent posts
    recent_posts = Post.query.filter_by(user_id=user.id).order_by(Post.created_at.desc()).limit(5).all()
    
    # Get user's campaigns
    campaigns = Campaign.query.filter_by(user_id=user.id).all()
    
    # Calculate stats
    total_posts = Post.query.filter_by(user_id=user.id).count()
    total_clicks = db.session.query(db.func.sum(Post.clicks)).filter_by(user_id=user.id).scalar() or 0
    
    return render_template('dashboard.html', 
                         user=user,
                         recent_posts=recent_posts,
                         campaigns=campaigns,
                         total_posts=total_posts,
                         total_clicks=total_clicks)

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
    user = current_user
    category = request.args.get('category', 'Electronics')
    
    # If user hasn't set up affiliate link, redirect to setup
    if not user.affiliate_link_base:
        flash('Please set up your Amazon affiliate link first!', 'warning')
        return redirect(url_for('setup'))
    
    scraper = AmazonProductScraper()
    
    # Get top products from Amazon
    try:
        products = scraper.get_top_products_by_category(category, limit=20)
        
        # Add affiliate links to products
        for product in products:
            if user.amazon_affiliate_id:
                product['affiliate_url'] = scraper.create_affiliate_url(
                    product['asin'], 
                    user.amazon_affiliate_id
                )
            else:
                # Use the short link format like amzn.to/44TOVc2
                product['affiliate_url'] = f"{user.affiliate_link_base}/{product['asin']}"
                
    except Exception as e:
        logger.error(f"Error fetching products: {e}")
        products = []
        flash('Unable to fetch products from Amazon. Please try again later.', 'error')
    
    categories = ['Electronics', 'Books', 'Home', 'Fashion', 'Health', 'Sports', 'Tools', 'Toys']
    
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

# ADMIN ROUTES - Money-making features for platform owner
@app.route('/admin')
@require_login
def admin_dashboard():
    """Admin dashboard - view all users and send email blasts"""
    if not current_user.is_admin:
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
@require_login
def admin_users():
    """View all user emails for marketing"""
    if not current_user.is_admin:
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

@app.route('/api/track-click/<int:post_id>')
def track_click(post_id):
    """Track clicks on affiliate links"""
    post = Post.query.get_or_404(post_id)
    post.clicks += 1
    db.session.commit()
    
    return redirect(post.affiliate_url)