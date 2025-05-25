"""
One-time migration script for Render database
Access /migrate endpoint to run database migration
"""
from flask import Flask, jsonify
import os
import psycopg2
from urllib.parse import urlparse

app = Flask(__name__)

@app.route('/')
def home():
    return '''
    <h1>Render Database Migration</h1>
    <p><a href="/migrate">Click here to run database migration</a></p>
    <p><strong>WARNING:</strong> Only run this once!</p>
    '''

@app.route('/migrate')
def migrate_database():
    database_url = os.environ.get('DATABASE_URL')
    if not database_url:
        return jsonify({"error": "DATABASE_URL not found"}), 500
    
    try:
        # Parse the database URL
        url = urlparse(database_url)
        
        # Connect to database
        conn = psycopg2.connect(
            host=url.hostname,
            port=url.port,
            database=url.path[1:],  # Remove leading slash
            user=url.username,
            password=url.password
        )
        cursor = conn.cursor()
        
        # List of ALL columns to add
        columns_to_add = [
            # Pinterest columns
            "ALTER TABLE users ADD COLUMN IF NOT EXISTS pinterest_access_token VARCHAR(500);",
            "ALTER TABLE users ADD COLUMN IF NOT EXISTS pinterest_board_id VARCHAR(500);",
            
            # Reddit columns
            "ALTER TABLE users ADD COLUMN IF NOT EXISTS reddit_client_id VARCHAR(500);",
            "ALTER TABLE users ADD COLUMN IF NOT EXISTS reddit_client_secret VARCHAR(500);",
            "ALTER TABLE users ADD COLUMN IF NOT EXISTS reddit_username VARCHAR(500);",
            "ALTER TABLE users ADD COLUMN IF NOT EXISTS reddit_password VARCHAR(500);",
            "ALTER TABLE users ADD COLUMN IF NOT EXISTS reddit_subreddit VARCHAR(500);",
            
            # Trial system columns
            "ALTER TABLE users ADD COLUMN IF NOT EXISTS trial_start_date TIMESTAMP;",
            "ALTER TABLE users ADD COLUMN IF NOT EXISTS trial_end_date TIMESTAMP;",
            "ALTER TABLE users ADD COLUMN IF NOT EXISTS trial_tier VARCHAR(20);",
            "ALTER TABLE users ADD COLUMN IF NOT EXISTS is_trial_active BOOLEAN DEFAULT FALSE;",
            "ALTER TABLE users ADD COLUMN IF NOT EXISTS premium_trial_used BOOLEAN DEFAULT FALSE;",
            "ALTER TABLE users ADD COLUMN IF NOT EXISTS pro_trial_used BOOLEAN DEFAULT FALSE;",
            "ALTER TABLE users ADD COLUMN IF NOT EXISTS contest_winner BOOLEAN DEFAULT FALSE;",
            "ALTER TABLE users ADD COLUMN IF NOT EXISTS subscription_start_date TIMESTAMP;",
            
            # Setup notification columns
            "ALTER TABLE users ADD COLUMN IF NOT EXISTS setup_notification_dismissed BOOLEAN DEFAULT FALSE;",
            "ALTER TABLE users ADD COLUMN IF NOT EXISTS setup_notification_dismissed_at TIMESTAMP;",
            
            # AI promotion columns
            "ALTER TABLE users ADD COLUMN IF NOT EXISTS last_ai_promotion_time TIMESTAMP;"
        ]
        
        results = []
        
        # Execute each migration
        for sql in columns_to_add:
            try:
                cursor.execute(sql)
                column_name = sql.split("ADD COLUMN IF NOT EXISTS")[1].split()[0]
                results.append(f"✅ Added column: {column_name}")
            except Exception as e:
                results.append(f"❌ Error adding column: {e}")
        
        # Commit changes
        conn.commit()
        results.append("🎉 Database migration completed successfully!")
        
        cursor.close()
        conn.close()
        
        return jsonify({
            "status": "success",
            "results": results
        })
        
    except Exception as e:
        return jsonify({
            "status": "error", 
            "error": str(e)
        }), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)