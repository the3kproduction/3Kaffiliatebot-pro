"""
Simple Email System for Product Sharing
Uses built-in email capabilities without requiring external API keys
"""
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
import requests
from models import User, ProductInventory

def create_product_email(product, user_email):
    """Create a beautiful HTML email for product promotion"""
    
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; background: #f5f5f5; margin: 0; padding: 20px; }}
            .container {{ max-width: 600px; margin: 0 auto; background: white; border-radius: 10px; overflow: hidden; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }}
            .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; text-align: center; }}
            .content {{ padding: 30px; }}
            .product-image {{ width: 100%; max-width: 400px; height: 300px; object-fit: contain; border-radius: 8px; margin: 20px 0; }}
            .price {{ font-size: 24px; color: #e74c3c; font-weight: bold; margin: 15px 0; }}
            .rating {{ color: #f39c12; font-size: 18px; margin: 10px 0; }}
            .buy-button {{ background: #ff9500; color: white; padding: 15px 30px; text-decoration: none; border-radius: 25px; display: inline-block; margin: 20px 0; font-weight: bold; }}
            .footer {{ background: #f8f9fa; padding: 20px; text-align: center; font-size: 14px; color: #666; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🎉 Amazing Product Deal!</h1>
                <p>Shared by {user_email}</p>
            </div>
            <div class="content">
                <h2>{product.get('title', 'Amazing Product')}</h2>
                <img src="{product.get('image_url', '')}" alt="Product Image" class="product-image">
                <div class="price">${product.get('price', '0.00')}</div>
                <div class="rating">⭐ {product.get('rating', '4.5')} stars</div>
                <p>This is an amazing deal I wanted to share with you! Check it out:</p>
                <a href="{product.get('affiliate_url', '')}" class="buy-button">🛒 View on Amazon</a>
                <p><small>This is an affiliate link - I may earn a small commission at no extra cost to you.</small></p>
            </div>
            <div class="footer">
                <p>Shared through AffiliateBot Pro</p>
                <p>This email was sent because you're on {user_email}'s sharing list.</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    return html_content

def send_product_email(product, from_email, to_emails):
    """
    Send product promotion email using simple mailto functionality
    This creates a pre-filled email that the user can send
    """
    try:
        # Create email subject and body
        subject = f"Amazing Deal: {product.get('title', 'Great Product')} - ${product.get('price', '0.00')}"
        
        # Simple text version for email clients
        body = f"""
Hi!

I found this amazing product and wanted to share it with you:

{product.get('title', 'Amazing Product')}
Price: ${product.get('price', '0.00')}
Rating: ⭐ {product.get('rating', '4.5')} stars

Check it out here: {product.get('affiliate_url', '')}

This is an affiliate link - I may earn a small commission at no extra cost to you.

Best regards!
        """
        
        # Create mailto link for easy sharing
        mailto_link = f"mailto:{';'.join(to_emails)}?subject={subject}&body={body.replace(' ', '%20').replace('\n', '%0A')}"
        
        return {
            'success': True,
            'mailto_link': mailto_link,
            'subject': subject,
            'body': body,
            'html_content': create_product_email(product, from_email)
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }

def share_product_via_email(user, product):
    """Share a product via email using user's configured email list"""
    try:
        if not user.email_configured or not user.email_list:
            return {'success': False, 'error': 'Email not configured'}
        
        # Parse email list
        email_list = [email.strip() for email in user.email_list.split(',') if email.strip()]
        
        if not email_list:
            return {'success': False, 'error': 'No emails in list'}
        
        # Create product dict for email
        product_dict = {
            'title': product.product_title,
            'price': product.price,
            'rating': product.rating,
            'image_url': product.image_url,
            'affiliate_url': f"https://www.amazon.com/dp/{product.asin}?tag=luxoraconnect-20"
        }
        
        # Send email
        result = send_product_email(product_dict, user.user_email, email_list)
        
        if result['success']:
            print(f"✅ Email prepared for {len(email_list)} recipients")
            return result
        else:
            return result
            
    except Exception as e:
        return {'success': False, 'error': str(e)}