import os

# Set environment flag for Render deployment early
if not os.environ.get('REPL_ID'):
    os.environ['RENDER'] = 'true'

from app import app

# Only import routes if we have Replit auth available
try:
    if os.environ.get('REPL_ID'):
        import routes  # noqa: F401
    else:
        # Use minimal routes for Render
        from flask import render_template
        from flask_login import login_user
        from simple_auth import create_demo_user
        
        @app.route('/')
        def index():
            demo_user = create_demo_user()
            login_user(demo_user)
            return "<h1>AffiliateBot Pro - Render Deployment</h1><p>Demo user auto-logged in!</p>"
        
except Exception as e:
    print(f"Route import error: {e}")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)