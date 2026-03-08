from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail, EmailMultiAlternatives
from django.conf import settings
from smtplib import SMTPException
import logging

# Set up logging
logger = logging.getLogger(__name__)

def send_email(subject, text_message, html_message, recipient_email):
    """
    Helper function to send an email with both plain-text and HTML content.
    """
    try:
        # Create the email with both plain-text and HTML versions
        email = EmailMultiAlternatives(
            subject=subject,
            body=text_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[recipient_email],
        )
        email.attach_alternative(html_message, "text/html")
        email.send(fail_silently=False)
        logger.info(f"Email sent successfully to {recipient_email}")
        return True
    except SMTPException as e:
        logger.error(f"SMTP error sending email to {recipient_email}: {e}")
    except Exception as e:
        logger.error(f"Unexpected error sending email to {recipient_email}: {e}")
    return False

def build_password_reset_link(user, request):
    """
    Build the password reset URL using the user's ID and token.
    """
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = default_token_generator.make_token(user)
    reset_link = request.build_absolute_uri(f"/accounts/set-password/{uid}/{token}/")
    return reset_link

def send_password_reset_link(user, reset_link, password=None):
    """
    Send password reset link to user via email.
    """

    # Email subject
    subject = "Set Up Your MzansiLogistics Password"

    # Plain text message
    text_message = f"""
    Hello {user.first_name},

    You've been invited to Mzansi Logistics or requested a password reset.
    
    Please click the link below to set your password:
    {reset_link}

    If you wish to continue with the current password: {password}

    This link will expire in 15 minutes for security reasons.

    If you didn't request this, please ignore this email.

    Best regards,
    The Mzansi Logistics Team
    """

    # HTML message
    html_message = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{
                font-family: Arial, sans-serif;
                line-height: 1.6;
                color: #333;
            }}
            .container {{
                maxInlineSize: 600px;
                margin: 0 auto;
                padding: 20px;
            }}
            .header {{
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 30px;
                text-align: center;
                border-radius: 10px 10px 0 0;
            }}
            .content {{
                background: #f9f9f9;
                padding: 30px;
                border-radius: 0 0 10px 10px;
            }}
            .button {{
                display: inline-block;
                padding: 12px 30px;
                background: #667eea;
                color: white;
                text-decoration: none;
                border-radius: 5px;
                margin: 20px 0;
            }}
            .footer {{
                text-align: center;
                marginBlockStart: 20px;
                color: #666;
                font-size: 12px;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>Mzansi Logistics</h1>
                <p>Fast . Reliable . Easy</p>
            </div>
            <div class="content">
                <h2>Hello {user.first_name},</h2>
                <p>You've been invited to Mzansi Logistics or requested a password reset.</p>
                <p>Click the button below to set your password:</p>
                <a href="{reset_link}" class="button">Set Password</a>
                <p>Or copy and paste this link into your browser:</p>
                <p style="word-break: break-all; color: #667eea;">{reset_link}</p>
                <p><strong>This link will expire in 15 minutes for security reasons.</strong></p>
                <p>If you wish to continue with the current password (Do NOT Share With Anyone): {password}</p>
                <p>If you didn't request this, please ignore this email.</p>
            </div>
            <div class="footer">
                <p>Best regards,<br>The Mzansi Logistics Team</p>
                <p>&copy; 2025 Mzansi Logistics. All rights reserved.</p>
            </div>
        </div>
    </body>
    </html>
    """

    # Send the email using the helper function
    return send_email(subject, text_message, html_message, user.email)

def send_welcome_email(user):
    """
    Send welcome email when the account is created.
    """
    subject = "Welcome to Mzansi Logistics!"
    
    text_message = f"""
    Hello {user.first_name},

    Welcome to Mzansi Logistics! Your account has been successfully created.

    You'll receive a separate email with instructions to set your password.

    Best regards,
    The Mzansi Logistics Team
    """

    html_message = f"""
    <!DOCTYPE html>
    <html>
    <body style="font-family: Arial, sans-serif;">
        <div style="maxInlineSize: 600px; margin: 0 auto; padding: 20px;">
            <h2 style="color: #667eea;">Welcome to Mzansi Logistics!</h2>
            <p>Hello {user.first_name},</p>
            <p>Welcome to Mzansi Logistics! Your account has been successfully created.</p>
            <p>You'll receive a separate email with instructions to set your password.</p>
            <p>Best regards,<br>The Mzansi Logistics Team</p>
        </div>
    </body>
    </html>
    """

    # Send the welcome email using the helper function
    return send_email(subject, text_message, html_message, user.email)

def get_monthly_data(year):
    """Get sales for each month in a year"""
    try:
        from django.db.models.functions import ExtractMonth
        from django.db.models import Sum
        # from finance.models import Invoice
       
        # invoiced = Invoice.objects.filter(
        #     date_field__year=year
        # ).annotate(
        #     month=ExtractMonth('date_field')
        # ).values('month').annotate(
        #     sum=Sum('total_amount')
        # ).order_by('month')
        
        # return {
        #     'invoiced': [
        #         {'id': inv.id, 'amount': inv.sum, 'month': inv.month} for inv in invoiced
        #     ],
        #     'paid':  [
        #         {'id': inv.id, 'amount': inv.sum, 'month': inv.month}  for inv in invoiced if inv.balance == 0
        #     ],
        #     'balance': [
        #         {'id': inv.id, 'amount': inv.sum, 'month': inv.month}  for inv in invoiced if inv.balance > 0
        #     ],
        # }
    except Exception as e:
        return None
