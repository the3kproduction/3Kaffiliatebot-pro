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