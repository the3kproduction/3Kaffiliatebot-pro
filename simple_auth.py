"""
Simple authentication system for Render deployment
Replaces Replit OAuth when REPL_ID is not available
"""
import os
from flask import session, redirect, url_for, request
from flask_login import LoginManager, login_user, logout_user, current_user
from functools import wraps
from app import app, db
from models import User

# Initialize Flask-Login
login_manager = LoginManager(app)
login_manager.login_view = 'index'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)

def create_demo_user():
    """Create a demo user for Render deployment"""
    demo_user = User.query.filter_by(id='demo-user').first()
    if not demo_user:
        demo_user = User(
            id='demo-user',
            email='demo@affiliatebot.com',
            first_name='Demo',
            last_name='User',
            is_admin=True,
            subscription_tier='pro'  # Give demo user pro access
        )
        db.session.add(demo_user)
        db.session.commit()
    return demo_user

def simple_require_login(f):
    """Simple login requirement for Render deployment"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            # Auto-login demo user on Render
            if os.environ.get('RENDER'):
                demo_user = create_demo_user()
                login_user(demo_user)
            else:
                return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function