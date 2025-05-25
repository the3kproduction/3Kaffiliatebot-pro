"""
Webhook Manager - Handle multiple destinations and testing
"""
import requests
import json
from datetime import datetime
from app import db
from models import WebhookDestination


class WebhookManager:
    def __init__(self, user):
        self.user = user
    
    def add_webhook_destination(self, name, platform, webhook_url, frequency_hours=3):
        """Add a new webhook destination"""
        destination = WebhookDestination(
            user_id=self.user.id,
            name=name,
            platform=platform.lower(),
            webhook_url=webhook_url,
            post_frequency_hours=frequency_hours
        )
        db.session.add(destination)
        db.session.commit()
        return destination
    
    def get_user_webhooks(self):
        """Get all webhook destinations for user"""
        return WebhookDestination.query.filter_by(
            user_id=self.user.id,
            is_active=True
        ).all()
    
    def test_webhook(self, webhook_id):
        """Test a webhook with a sample message"""
        webhook = WebhookDestination.query.filter_by(
            id=webhook_id,
            user_id=self.user.id
        ).first()
        
        if not webhook:
            return {"success": False, "error": "Webhook not found"}
        
        test_message = self._create_test_message(webhook.platform)
        
        try:
            response = requests.post(
                webhook.webhook_url,
                json=test_message,
                timeout=10
            )
            
            success = response.status_code in [200, 204]
            
            # Update test results
            webhook.last_test_time = datetime.now()
            webhook.last_test_success = success
            db.session.commit()
            
            return {
                "success": success,
                "status_code": response.status_code,
                "response": response.text[:200] if not success else "Test successful!"
            }
            
        except Exception as e:
            webhook.last_test_time = datetime.now()
            webhook.last_test_success = False
            db.session.commit()
            
            return {"success": False, "error": str(e)}
    
    def post_to_webhook(self, webhook_id, product_data):
        """Post product to specific webhook"""
        webhook = WebhookDestination.query.filter_by(
            id=webhook_id,
            user_id=self.user.id,
            is_active=True
        ).first()
        
        if not webhook:
            return {"success": False, "error": "Webhook not found or inactive"}
        
        message = self._create_product_message(webhook.platform, product_data)
        
        try:
            response = requests.post(
                webhook.webhook_url,
                json=message,
                timeout=10
            )
            
            success = response.status_code in [200, 204]
            
            if success:
                webhook.last_post_time = datetime.now()
                db.session.commit()
            
            return {
                "success": success,
                "webhook_name": webhook.name,
                "platform": webhook.platform
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _create_test_message(self, platform):
        """Create test message for platform"""
        if platform == 'discord':
            return {
                "content": "🔥 **Webhook Test Successful!** 🔥\n\nYour AffiliateBot Pro webhook is working perfectly! Ready to start promoting amazing products and earning commissions! 💰"
            }
        elif platform == 'slack':
            return {
                "text": "🔥 Webhook Test Successful! 🔥\n\nYour AffiliateBot Pro webhook is working perfectly! Ready to start promoting amazing products and earning commissions! 💰"
            }
        else:  # Generic webhook
            return {
                "message": "Webhook test successful - AffiliateBot Pro is ready!",
                "status": "connected"
            }
    
    def _create_product_message(self, platform, product):
        """Create product promotion message for platform"""
        base_message = f"""
🔥 **AMAZING DEAL ALERT!** 🔥

📦 **{product.get('title', 'Hot Product')}**
⭐ Rating: {product.get('rating', 'N/A')}/5
💰 Price: {product.get('price', 'Check link')}

🛒 **GET IT NOW:** {product.get('affiliate_url', '')}

#affiliate #deals #amazon #savings
        """.strip()
        
        if platform == 'discord':
            return {"content": base_message}
        elif platform == 'slack':
            return {"text": base_message}
        else:  # Generic webhook
            return {
                "message": base_message,
                "product": product,
                "timestamp": datetime.now().isoformat()
            }
    
    def get_webhook_status(self, webhook_id):
        """Get status indicators for webhook"""
        webhook = WebhookDestination.query.get(webhook_id)
        if not webhook:
            return None
        
        status = {
            "id": webhook.id,
            "name": webhook.name,
            "platform": webhook.platform,
            "is_active": webhook.is_active,
            "last_test_success": webhook.last_test_success,
            "last_test_time": webhook.last_test_time,
            "last_post_time": webhook.last_post_time,
            "color": "green" if webhook.last_test_success else "red" if webhook.last_test_time else "gray"
        }
        
        return status