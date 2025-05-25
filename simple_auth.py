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
    """Create admin user with specified credentials"""
    admin_user = User.query.filter_by(email='the3kproduction@gmail.com').first()
    if not admin_user:
        admin_user = User(
            id='admin-3kloudz',
            email='the3kproduction@gmail.com',
            username='3Kloudz',
            first_name='3K',
            last_name='Production',
            is_admin=True,
            subscription_tier='lifetime',
            amazon_affiliate_id='luxoraconnect-20'
        )
        db.session.add(admin_user)
        db.session.commit()
    return admin_user

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