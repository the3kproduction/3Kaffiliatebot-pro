"""
Automated Product Catalog Updater
Runs daily to refresh your product catalog with trending Amazon products
Keeps your affiliate marketing content fresh and profitable
"""
import schedule
import time
from datetime import datetime
from amazon_bestsellers_scraper import run_trending_update

def update_product_catalog():
    """Update product catalog with fresh trending products"""
    print(f"🕐 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - Starting product catalog update...")
    
    try:
        updated_count = run_trending_update()
        print(f"✅ Successfully updated catalog with {updated_count} trending products!")
        
        # Log the update
        with open('product_update_log.txt', 'a') as f:
            f.write(f"{datetime.now().isoformat()} - Updated {updated_count} products\n")
            
    except Exception as e:
        print(f"❌ Error updating product catalog: {e}")
        
        # Log the error
        with open('product_update_log.txt', 'a') as f:
            f.write(f"{datetime.now().isoformat()} - ERROR: {e}\n")

def start_auto_updater():
    """Start the automated product updater"""
    print("🚀 Starting automated product catalog updater...")
    print("📅 Schedule: Updates every day at 6:00 AM")
    print("🎯 Goal: Keep your catalog fresh with trending Amazon products")
    
    # Schedule daily updates at 6 AM
    schedule.every().day.at("06:00").do(update_product_catalog)
    
    # Also allow manual updates every 6 hours if needed
    schedule.every(6).hours.do(update_product_catalog)
    
    print("✅ Auto-updater started! Your products will stay fresh automatically.")
    
    # Run initial update
    update_product_catalog()
    
    # Keep running
    while True:
        schedule.run_pending()
        time.sleep(3600)  # Check every hour

if __name__ == '__main__':
    start_auto_updater()