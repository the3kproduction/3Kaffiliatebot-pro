"""
Ultra-simple Flask app for Render deployment
No database dependencies, just works!
"""
from flask import Flask, render_template_string, jsonify
import os

app = Flask(__name__)
app.secret_key = "simple-render-key"

# Simple HTML templates as strings to avoid template issues
LANDING_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <title>AffiliateBot Pro - Amazon Affiliate Marketing Automation</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: 'Segoe UI', sans-serif; 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            color: white;
        }
        .hero { 
            padding: 4rem 2rem; 
            text-align: center; 
            max-width: 1200px; 
            margin: 0 auto; 
        }
        h1 { font-size: 3.5rem; margin-bottom: 1rem; }
        .subtitle { font-size: 1.5rem; margin-bottom: 3rem; opacity: 0.9; }
        .features { 
            display: grid; 
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); 
            gap: 2rem; 
            margin: 3rem 0; 
        }
        .feature { 
            background: rgba(255,255,255,0.1); 
            padding: 2rem; 
            border-radius: 15px; 
            backdrop-filter: blur(10px); 
        }
        .cta { 
            background: #ff6b35; 
            color: white; 
            padding: 1rem 2rem; 
            border: none; 
            border-radius: 50px; 
            font-size: 1.2rem; 
            cursor: pointer; 
            text-decoration: none; 
            display: inline-block; 
            margin: 1rem; 
        }
        .cta:hover { background: #e55a2b; }
        .stats { 
            display: flex; 
            justify-content: center; 
            gap: 3rem; 
            margin: 3rem 0; 
        }
        .stat { text-align: center; }
        .stat-number { font-size: 2.5rem; font-weight: bold; }
        .stat-label { opacity: 0.8; }
    </style>
</head>
<body>
    <div class="hero">
        <h1>🚀 AffiliateBot Pro</h1>
        <p class="subtitle">Automate Your Amazon Affiliate Marketing Across 10+ Platforms</p>
        
        <div class="stats">
            <div class="stat">
                <div class="stat-number">1,247+</div>
                <div class="stat-label">Posts Automated</div>
            </div>
            <div class="stat">
                <div class="stat-number">$2,156</div>
                <div class="stat-label">Revenue Generated</div>
            </div>
            <div class="stat">
                <div class="stat-number">12.8%</div>
                <div class="stat-label">Conversion Rate</div>
            </div>
        </div>

        <div class="features">
            <div class="feature">
                <h3>🎯 AI-Powered Product Selection</h3>
                <p>Our AI automatically finds trending Amazon products and creates engaging posts that convert.</p>
            </div>
            <div class="feature">
                <h3>📱 Multi-Platform Posting</h3>
                <p>Post to Discord, Telegram, Slack, Email, Pinterest, Reddit, Twitter, and more - all automatically.</p>
            </div>
            <div class="feature">
                <h3>💰 Subscription Tiers</h3>
                <p>Free (2 posts/day), Premium (8 posts/day), Pro (24 posts/day) - scale as you grow!</p>
            </div>
            <div class="feature">
                <h3>📊 Real-Time Analytics</h3>
                <p>Track clicks, conversions, and revenue with our comprehensive dashboard.</p>
            </div>
        </div>

        <a href="/demo" class="cta">🎯 Try Demo</a>
        <a href="/signup" class="cta">🚀 Start Free</a>
    </div>
</body>
</html>
"""

DEMO_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <title>Demo - AffiliateBot Pro Dashboard</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: 'Segoe UI', sans-serif; 
            background: #f5f7fa; 
            padding: 2rem; 
        }
        .dashboard { 
            max-width: 1200px; 
            margin: 0 auto; 
            background: white; 
            border-radius: 15px; 
            padding: 2rem; 
            box-shadow: 0 10px 30px rgba(0,0,0,0.1); 
        }
        .header { 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
            color: white; 
            padding: 2rem; 
            border-radius: 10px; 
            margin-bottom: 2rem; 
        }
        .metrics { 
            display: grid; 
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); 
            gap: 1.5rem; 
            margin-bottom: 2rem; 
        }
        .metric { 
            background: #f8f9fc; 
            padding: 1.5rem; 
            border-radius: 10px; 
            text-align: center; 
        }
        .metric-value { 
            font-size: 2rem; 
            font-weight: bold; 
            color: #333; 
        }
        .metric-label { 
            color: #666; 
            margin-top: 0.5rem; 
        }
        .recent-posts { 
            background: #f8f9fc; 
            padding: 1.5rem; 
            border-radius: 10px; 
        }
        .post-item { 
            background: white; 
            margin: 1rem 0; 
            padding: 1rem; 
            border-radius: 8px; 
            border-left: 4px solid #667eea; 
        }
        .platforms { 
            display: flex; 
            gap: 0.5rem; 
            margin-top: 0.5rem; 
        }
        .platform-badge { 
            background: #667eea; 
            color: white; 
            padding: 0.25rem 0.5rem; 
            border-radius: 4px; 
            font-size: 0.8rem; 
        }
    </style>
</head>
<body>
    <div class="dashboard">
        <div class="header">
            <h1>📊 AffiliateBot Pro Dashboard</h1>
            <p>Live demo showing your automated affiliate marketing performance</p>
        </div>

        <div class="metrics">
            <div class="metric">
                <div class="metric-value">1,247</div>
                <div class="metric-label">Total Posts</div>
            </div>
            <div class="metric">
                <div class="metric-value">$2,156</div>
                <div class="metric-label">Revenue</div>
            </div>
            <div class="metric">
                <div class="metric-value">8,934</div>
                <div class="metric-label">Total Clicks</div>
            </div>
            <div class="metric">
                <div class="metric-value">12.8%</div>
                <div class="metric-label">Conversion Rate</div>
            </div>
        </div>

        <div class="recent-posts">
            <h3>🔥 Recent Automated Posts</h3>
            
            <div class="post-item">
                <strong>Wireless Bluetooth Headphones - $49.99</strong>
                <p>AI-generated post: "🎧 Game-changing sound quality! These wireless headphones are flying off the shelves..."</p>
                <div class="platforms">
                    <span class="platform-badge">Discord</span>
                    <span class="platform-badge">Telegram</span>
                    <span class="platform-badge">Email</span>
                </div>
            </div>

            <div class="post-item">
                <strong>Smart Home Security Camera - $89.99</strong>
                <p>AI-generated post: "🏠 Protect what matters most! This security camera just hit an amazing price..."</p>
                <div class="platforms">
                    <span class="platform-badge">Slack</span>
                    <span class="platform-badge">Reddit</span>
                    <span class="platform-badge">Pinterest</span>
                </div>
            </div>

            <div class="post-item">
                <strong>Portable Phone Charger - $24.99</strong>
                <p>AI-generated post: "⚡ Never run out of battery again! This power bank is a lifesaver..."</p>
                <div class="platforms">
                    <span class="platform-badge">Twitter</span>
                    <span class="platform-badge">Facebook</span>
                    <span class="platform-badge">Discord</span>
                </div>
            </div>
        </div>
    </div>
</body>
</html>
"""

@app.route('/')
def landing():
    """Landing page"""
    return render_template_string(LANDING_PAGE)

@app.route('/demo')
def demo():
    """Demo dashboard"""
    return render_template_string(DEMO_PAGE)

@app.route('/signup')
def signup():
    """Signup redirect"""
    return """
    <html>
    <head>
        <title>Sign Up - AffiliateBot Pro</title>
        <style>
            body { 
                font-family: Arial, sans-serif; 
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                display: flex; justify-content: center; align-items: center; 
                height: 100vh; margin: 0; color: white; text-align: center; 
            }
            .signup-box { 
                background: rgba(255,255,255,0.1); 
                padding: 3rem; border-radius: 20px; 
                backdrop-filter: blur(10px); 
            }
        </style>
    </head>
    <body>
        <div class="signup-box">
            <h2>🚀 Ready to Start?</h2>
            <p>Your affiliate marketing platform is ready!</p>
            <p style="margin-top: 2rem;">
                <a href="/" style="color: #ff6b35;">← Back to Home</a>
            </p>
        </div>
    </body>
    </html>
    """

@app.route('/api/stats')
def api_stats():
    """API endpoint for stats"""
    return jsonify({
        'total_posts': 1247,
        'revenue': 2156.43,
        'clicks': 8934,
        'conversion_rate': 12.8,
        'status': 'success'
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)