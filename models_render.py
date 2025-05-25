from datetime import datetime

from app import db
from flask_dance.consumer.storage.sqla import OAuthConsumerMixin
from flask_login import UserMixin
from sqlalchemy import UniqueConstraint


# Minimal User model that only uses columns that exist in Render database
class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.String, primary_key=True)
    email = db.Column(db.String, unique=True, nullable=True)
    first_name = db.Column(db.String, nullable=True)
    last_name = db.Column(db.String, nullable=True)
    profile_image_url = db.Column(db.String, nullable=True)

    # Amazon affiliate settings
    amazon_affiliate_id = db.Column(db.String, nullable=True)
    affiliate_link_base = db.Column(db.String, nullable=True)

    # Platform integration settings
    discord_webhook_url = db.Column(db.String, nullable=True)
    telegram_bot_token = db.Column(db.String, nullable=True)
    telegram_chat_id = db.Column(db.String, nullable=True)
    slack_bot_token = db.Column(db.String, nullable=True)
    slack_channel_id = db.Column(db.String, nullable=True)

    # Email settings
    sendgrid_api_key = db.Column(db.String, nullable=True)
    email_from = db.Column(db.String, nullable=True)
    email_to = db.Column(db.String, nullable=True)

    # Automation settings
    auto_post_enabled = db.Column(db.Boolean, default=False)
    post_frequency_hours = db.Column(db.Integer, default=3)

    # User management
    is_admin = db.Column(db.Boolean, default=False)
    subscription_tier = db.Column(db.String(20), default='free')
    email_notifications = db.Column(db.Boolean, default=True)

    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)

    # Relationships
    campaigns = db.relationship('Campaign', backref='user', lazy=True, cascade='all, delete-orphan')
    posts = db.relationship('Post', backref='user', lazy=True, cascade='all, delete-orphan')

    def __repr__(self):
        return f'<User {self.email}>'

    @property
    def display_name(self):
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        elif self.first_name:
            return self.first_name
        elif self.email:
            return self.email.split('@')[0]
        return "User"

    # Helper methods for subscription tiers
    def can_use_ai_promotions(self):
        return self.subscription_tier in ['premium', 'pro', 'lifetime']

    def get_daily_post_limit(self):
        limits = {
            'free': 2,
            'premium': 8,
            'pro': 24,
            'lifetime': 50
        }
        return limits.get(self.subscription_tier, 2)


# OAuth model for authentication
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


# Campaign model
class Campaign(db.Model):
    __tablename__ = 'campaigns'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String, db.ForeignKey('users.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    category = db.Column(db.String(50))
    is_active = db.Column(db.Boolean, default=True)

    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)

    posts = db.relationship('Post', backref='campaign', lazy=True)

    def __repr__(self):
        return f'<Campaign {self.name}>'


# Post model
class Post(db.Model):
    __tablename__ = 'posts'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String, db.ForeignKey('users.id'), nullable=False)
    campaign_id = db.Column(db.Integer, db.ForeignKey('campaigns.id'), nullable=True)

    # Product information
    product_title = db.Column(db.String(200), nullable=False)
    product_description = db.Column(db.Text)
    product_image_url = db.Column(db.String(500))
    amazon_url = db.Column(db.String(500), nullable=False)
    affiliate_url = db.Column(db.String(500), nullable=False)
    price = db.Column(db.String(20))
    rating = db.Column(db.Float)
    category = db.Column(db.String(50))

    asin = db.Column(db.String(20))

    # Platform posting status
    posted_to_discord = db.Column(db.Boolean, default=False)
    discord_posted_at = db.Column(db.DateTime, nullable=True)
    posted_to_telegram = db.Column(db.Boolean, default=False)
    telegram_posted_at = db.Column(db.DateTime, nullable=True)
    posted_to_slack = db.Column(db.Boolean, default=False)
    slack_posted_at = db.Column(db.DateTime, nullable=True)
    posted_to_email = db.Column(db.Boolean, default=False)
    email_posted_at = db.Column(db.DateTime, nullable=True)

    # Analytics
    clicks = db.Column(db.Integer, default=0)
    impressions = db.Column(db.Integer, default=0)
    conversion_rate = db.Column(db.Float, default=0.0)
    revenue_estimated = db.Column(db.Float, default=0.0)

    # Scheduling
    scheduled_for = db.Column(db.DateTime, nullable=True)
    is_scheduled = db.Column(db.Boolean, default=False)

    created_at = db.Column(db.DateTime, default=datetime.now)

    def __repr__(self):
        return f'<Post {self.product_title[:30]}...>'


# Product inventory
class ProductInventory(db.Model):
    __tablename__ = 'product_inventory'
    id = db.Column(db.Integer, primary_key=True)
    asin = db.Column(db.String(20), unique=True, nullable=False)
    product_title = db.Column(db.String(200), nullable=False)
    category = db.Column(db.String(50))
    price = db.Column(db.String(20))
    rating = db.Column(db.Float)
    image_url = db.Column(db.String(500))

    times_promoted = db.Column(db.Integer, default=0)
    last_promoted = db.Column(db.DateTime, nullable=True)
    total_clicks = db.Column(db.Integer, default=0)
    conversion_rate = db.Column(db.Float, default=0.0)

    is_active = db.Column(db.Boolean, default=True)
    is_trending = db.Column(db.Boolean, default=False)

    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)


# User product promotions tracking
class UserProductPromotion(db.Model):
    __tablename__ = 'user_product_promotions'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String, db.ForeignKey('users.id'), nullable=False)
    asin = db.Column(db.String(20), db.ForeignKey('product_inventory.asin'), nullable=False)

    promoted_at = db.Column(db.DateTime, default=datetime.now)
    platform = db.Column(db.String(20))
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'), nullable=True)

    clicks_generated = db.Column(db.Integer, default=0)
    revenue_generated = db.Column(db.Float, default=0.0)

    user = db.relationship('User', backref='product_promotions')
    product = db.relationship('ProductInventory', backref='user_promotions')

    __table_args__ = (UniqueConstraint('user_id', 'asin', name='uq_user_product'),)