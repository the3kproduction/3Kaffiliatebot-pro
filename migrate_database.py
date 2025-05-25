#!/usr/bin/env python3
"""
Database Migration Script for Render Deployment
Adds missing Pinterest and Reddit columns to the users table
"""
import os
import psycopg2
from urllib.parse import urlparse

def migrate_database():
    # Get database URL from environment
    database_url = os.environ.get('DATABASE_URL')
    if not database_url:
        print("ERROR: DATABASE_URL environment variable not found")
        return False
    
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
        
        print("Connected to database successfully")
        
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
        
        # Execute each migration
        for sql in columns_to_add:
            try:
                cursor.execute(sql)
                column_name = sql.split("ADD COLUMN IF NOT EXISTS")[1].split()[0]
                print(f"✅ Added column: {column_name}")
            except Exception as e:
                print(f"❌ Error adding column: {e}")
        
        # Commit changes
        conn.commit()
        print("🎉 Database migration completed successfully!")
        
        # Verify columns exist
        cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'users' 
            AND (column_name LIKE '%pinterest%' OR column_name LIKE '%reddit%' 
                 OR column_name LIKE '%trial%' OR column_name LIKE '%notification%'
                 OR column_name = 'last_ai_promotion_time' OR column_name = 'contest_winner'
                 OR column_name = 'subscription_start_date')
            ORDER BY column_name;
        """)
        
        columns = cursor.fetchall()
        print("\n📋 Verified columns:")
        for col in columns:
            print(f"  - {col[0]}")
        
        cursor.close()
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Database migration failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Starting database migration...")
    success = migrate_database()
    if success:
        print("✅ Migration completed successfully!")
    else:
        print("❌ Migration failed!")