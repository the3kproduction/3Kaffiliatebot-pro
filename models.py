from datetime import datetime
from app import db
from flask_dance.consumer.storage.sqla import OAuthConsumerMixin
from flask_login import UserMixin
from sqlalchemy import UniqueConstraint

# User authentication tables (required for Replit Auth)
class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.String, primary_key=True)
    email = db.Column(db.String, unique=True, nullable=True)
    first_name = db.Column(db.String, nullable=True)
    last_name = db.Column(db.String, nullable=True)
    profile_image_url = db.Column(db.String, nullable=True)
    
    # Affiliate marketing fields
    amazon_affiliate_id = db.Column(db.String, nullable=True)
    affiliate_link_base = db.Column(db.String, nullable=True)  # e.g., "amzn.to/44TOVc2"
    
    # Platform preferences
    discord_webhook_url = db.Column(db.String, nullable=True)
    telegram_bot_token = db.Column(db.String, nullable=True)
    telegram_chat_id = db.Column(db.String, nullable=True)
    slack_bot_token = db.Column(db.String, nullable=True)
    slack_channel_id = db.Column(db.String, nullable=True)
    sendgrid_api_key = db.Column(db.String, nullable=True)
    email_from = db.Column(db.String, nullable=True)
    email_to = db.Column(db.String, nullable=True)
    
    # Automation settings
    auto_post_enabled = db.Column(db.Boolean, default=False)
    post_frequency_hours = db.Column(db.Integer, default=3)
    
    # Admin and subscription fields
    is_admin = db.Column(db.Boolean, default=False)
    subscription_tier = db.Column(db.String(20), default='free')  # free, premium, pro
    email_notifications = db.Column(db.Boolean, default=True)
    
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    
    # Relationships
    campaigns = db.relationship('Campaign', backref='user', lazy=True, cascade='all, delete-orphan')
    posts = db.relationship('Post', backref='user', lazy=True, cascade='all, delete-orphan')

class OAuth(OAuthConsumerMixin, db.Model):
    user_id = db.Column(db.String, db.ForeignKey(User.id))
    browser_session_key = db.Column(db.String, nullable=False)
    user = db.relationship(User)

    __table_args__ = (UniqueConstraint(
        'user_id',
        'browser_session_key',
        'provider',
        name='uq_user_browser_session_key_provider',
    ),)

# Campaign tracking
class Campaign(db.Model):
    __tablename__ = 'campaigns'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String, db.ForeignKey('users.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    category = db.Column(db.String(50))  # Electronics, Books, etc.
    is_active = db.Column(db.Boolean, default=True)
    
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    
    # Relationships
    posts = db.relationship('Post', backref='campaign', lazy=True)

# Post tracking and analytics
class Post(db.Model):
    __tablename__ = 'posts'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String, db.ForeignKey('users.id'), nullable=False)
    campaign_id = db.Column(db.Integer, db.ForeignKey('campaigns.id'), nullable=True)
    
    # Amazon product info
    product_title = db.Column(db.String(200), nullable=False)
    product_description = db.Column(db.Text)
    product_image_url = db.Column(db.String(500))
    amazon_url = db.Column(db.String(500), nullable=False)
    affiliate_url = db.Column(db.String(500), nullable=False)
    price = db.Column(db.String(20))
    rating = db.Column(db.Float)
    category = db.Column(db.String(50))
    
    # Product tracking
    asin = db.Column(db.String(20))  # For duplicate tracking
    
    # Platform posting status with timestamps
    posted_to_discord = db.Column(db.Boolean, default=False)
    discord_posted_at = db.Column(db.DateTime, nullable=True)
    posted_to_telegram = db.Column(db.Boolean, default=False)
    telegram_posted_at = db.Column(db.DateTime, nullable=True)
    posted_to_slack = db.Column(db.Boolean, default=False)
    slack_posted_at = db.Column(db.DateTime, nullable=True)
    posted_to_email = db.Column(db.Boolean, default=False)
    email_posted_at = db.Column(db.DateTime, nullable=True)
    
    # Enhanced Analytics
    clicks = db.Column(db.Integer, default=0)
    impressions = db.Column(db.Integer, default=0)
    conversion_rate = db.Column(db.Float, default=0.0)
    revenue_estimated = db.Column(db.Float, default=0.0)
    
    # Scheduling
    scheduled_for = db.Column(db.DateTime, nullable=True)
    is_scheduled = db.Column(db.Boolean, default=False)
    
    created_at = db.Column(db.DateTime, default=datetime.now)
    
    def __repr__(self):
        return f'<Post {self.product_title}>'

# Email blast campaigns for admin
class EmailBlast(db.Model):
    __tablename__ = 'email_blasts'
    id = db.Column(db.Integer, primary_key=True)
    admin_user_id = db.Column(db.String, db.ForeignKey('users.id'), nullable=False)
    
    subject = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    target_tier = db.Column(db.String(20), default='all')  # all, free, premium, pro
    
    # Stats
    emails_sent = db.Column(db.Integer, default=0)
    emails_opened = db.Column(db.Integer, default=0)
    clicks = db.Column(db.Integer, default=0)
    
    sent_at = db.Column(db.DateTime, default=datetime.now)
    created_at = db.Column(db.DateTime, default=datetime.now)
    
    def __repr__(self):
        return f'<EmailBlast {self.subject}>'

# Product inventory tracking
class ProductInventory(db.Model):
    __tablename__ = 'product_inventory'
    id = db.Column(db.Integer, primary_key=True)
    asin = db.Column(db.String(20), unique=True, nullable=False)
    product_title = db.Column(db.String(200), nullable=False)
    category = db.Column(db.String(50))
    price = db.Column(db.String(20))
    rating = db.Column(db.Float)
    image_url = db.Column(db.String(500))
    
    # Tracking stats
    times_promoted = db.Column(db.Integer, default=0)
    last_promoted = db.Column(db.DateTime, nullable=True)
    total_clicks = db.Column(db.Integer, default=0)
    conversion_rate = db.Column(db.Float, default=0.0)
    
    # Status
    is_active = db.Column(db.Boolean, default=True)
    is_trending = db.Column(db.Boolean, default=False)
    
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)

# Multiple webhook destinations
class WebhookDestination(db.Model):
    __tablename__ = 'webhook_destinations'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String, db.ForeignKey('users.id'), nullable=False)
    
    name = db.Column(db.String(100), nullable=False)  # "Discord Sales Channel"
    platform = db.Column(db.String(20), nullable=False)  # discord, telegram, slack
    webhook_url = db.Column(db.String(500), nullable=False)
    
    # Configuration
    is_active = db.Column(db.Boolean, default=True)
    post_frequency_hours = db.Column(db.Integer, default=3)
    last_post_time = db.Column(db.DateTime, nullable=True)
    
    # Testing
    last_test_time = db.Column(db.DateTime, nullable=True)
    last_test_success = db.Column(db.Boolean, default=False)
    
    created_at = db.Column(db.DateTime, default=datetime.now)