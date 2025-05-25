import os
import logging
from models import User
from app import db

logger = logging.getLogger(__name__)

def send_mass_email(email_blast):
    """Send email blast to targeted users"""
    try:
        from sendgrid import SendGridAPIClient
        from sendgrid.helpers.mail import Mail, To
        
        # Get SendGrid API key from admin settings or environment
        api_key = os.environ.get('SENDGRID_API_KEY')
        if not api_key:
            logger.error("SendGrid API key not configured")
            return 0
        
        # Get target users based on tier
        query = User.query.filter(User.email_notifications == True)
        if email_blast.target_tier != 'all':
            query = query.filter(User.subscription_tier == email_blast.target_tier)
        
        target_users = query.all()
        
        if not target_users:
            logger.warning("No target users found")
            return 0
        
        sg = SendGridAPIClient(api_key)
        emails_sent = 0
        
        # Send emails in batches to avoid rate limits
        batch_size = 100
        from_email = os.environ.get('EMAIL_FROM', 'noreply@affiliate-marketing.com')
        
        for i in range(0, len(target_users), batch_size):
            batch = target_users[i:i + batch_size]
            
            try:
                # Create email for batch
                to_emails = [user.email for user in batch if user.email]
                
                if not to_emails:
                    continue
                
                # Create personalized HTML content
                html_content = f"""
                <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 30px; text-align: center;">
                        <h1 style="color: white; margin: 0;">🚀 Amazon Affiliate Marketing Platform</h1>
                    </div>
                    
                    <div style="padding: 30px; background: white;">
                        {email_blast.content}
                    </div>
                    
                    <div style="background: #f8f9fa; padding: 20px; text-align: center; border-top: 1px solid #dee2e6;">
                        <p style="margin: 0; color: #6c757d; font-size: 14px;">
                            You're receiving this because you signed up for our Amazon affiliate marketing platform.
                            <br>
                            <a href="#unsubscribe" style="color: #6c757d;">Unsubscribe</a>
                        </p>
                    </div>
                </div>
                """
                
                message = Mail(
                    from_email=from_email,
                    to_emails=to_emails,
                    subject=email_blast.subject,
                    html_content=html_content
                )
                
                response = sg.send(message)
                
                if response.status_code == 202:
                    emails_sent += len(to_emails)
                    logger.info(f"Sent batch of {len(to_emails)} emails")
                else:
                    logger.error(f"Failed to send batch: {response.status_code}")
                    
            except Exception as e:
                logger.error(f"Error sending batch: {e}")
                continue
        
        logger.info(f"Mass email completed. Sent to {emails_sent} users")
        return emails_sent
        
    except ImportError:
        logger.error("SendGrid not installed")
        return 0
    except Exception as e:
        logger.error(f"Mass email failed: {e}")
        return 0