"""
Standalone Flask app for Render deployment - No authentication required
"""
from flask import Flask, render_template, jsonify
import os

app = Flask(__name__)
app.secret_key = "demo-key-for-render"

@app.route('/')
def landing_page():
    """Landing page for public demo"""
    return render_template('render_landing.html')

@app.route('/demo-dashboard')
def demo_dashboard():
    """Demo dashboard showing platform features"""
    return render_template('render_dashboard.html')

@app.route('/signup-free')
def signup_free():
    """Redirect to main platform for free tier signup"""
    # Get your main Replit app URL - replace with your actual domain
    main_platform_url = "https://3kaffiliatebot-pro-luxoraconnect-20.replit.app"
    return f'''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Redirecting to Free Signup...</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                display: flex;
                justify-content: center;
                align-items: center;
                height: 100vh;
                margin: 0;
                color: white;
                text-align: center;
            }}
            .redirect-box {{
                background: rgba(255, 255, 255, 0.1);
                backdrop-filter: blur(10px);
                padding: 3rem;
                border-radius: 20px;
                max-width: 500px;
            }}
            .spinner {{
                border: 4px solid rgba(255, 255, 255, 0.3);
                border-top: 4px solid white;
                border-radius: 50%;
                width: 40px;
                height: 40px;
                animation: spin 1s linear infinite;
                margin: 20px auto;
            }}
            @keyframes spin {{
                0% {{ transform: rotate(0deg); }}
                100% {{ transform: rotate(360deg); }}
            }}
        </style>
        <script>
            setTimeout(function() {{
                window.location.href = "{main_platform_url}/?signup=free";
            }}, 2000);
        </script>
    </head>
    <body>
        <div class="redirect-box">
            <h2>🚀 Welcome to AffiliateBot Pro!</h2>
            <p>Redirecting you to create your free account...</p>
            <div class="spinner"></div>
            <p><small>Free tier includes 2 posts per day, basic analytics, and Discord integration</small></p>
            <p><a href="{main_platform_url}/?signup=free" style="color: #ff6b35;">Click here if not redirected automatically</a></p>
        </div>
    </body>
    </html>
    '''

@app.route('/api/demo-stats')
def demo_stats():
    """Demo API endpoint for dashboard stats"""
    return jsonify({
        'total_posts': 1247,
        'total_clicks': 8934,
        'conversion_rate': 12.8,
        'revenue': 2156.43,
        'active_campaigns': 5,
        'platforms_connected': 6
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)