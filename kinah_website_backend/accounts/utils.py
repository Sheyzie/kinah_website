from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail, EmailMultiAlternatives
from django.conf import settings
from smtplib import SMTPException
import logging

from decimal import Decimal
from datetime import datetime
import uuid
import json

# Set up logging
logger = logging.getLogger(__name__)


def build_password_reset_link(user, request):
    """
    Build the password reset URL using the user's ID and token.
    """
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = default_token_generator.make_token(user)
    reset_link = request.build_absolute_uri(f"/accounts/set-password/{uid}/{token}/")
    return reset_link


class EmailService:

    def __init__(self, recipient_email, user=None, subject=None, text_message=None, html_message=None):
        self.recipient_email = recipient_email
        self.user = user
        self.subject = subject
        self.text_message = text_message
        self.html_message = html_message

    def send_email(self, subject=None, text_message=None, html_message=None):
        """
        Helper function to send an email with both plain-text and HTML content.
        """
        try:
            # Create the email with both plain-text and HTML versions
            email = EmailMultiAlternatives(
                subject=subject,
                body=text_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[self.recipient_email],
            )
            email.attach_alternative(html_message, "text/html")
            email.send(fail_silently=False)
            logger.info(f"Email sent successfully to {self.recipient_email}")
            return True
        except SMTPException as e:
            logger.error(f"SMTP error sending email to {self.recipient_email}: {e}")
        except Exception as e:
            logger.error(f"Unexpected error sending email to {self.recipient_email}: {e}")
        return False

    def send_password_reset_link(self, reset_link, password=None):
        """
        Send password reset link to user via email.
        """

        # Email subject
        subject = "Set Up Your Kinahs Password"

        # Plain text message
        text_message = f"""
        Hello {self.user.first_name},

        You've been invited to Kinah or requested a password reset.
        
        Please click the link below to set your password:
        {reset_link}

        This link will expire in 15 minutes for security reasons.

        If you didn't request this, please ignore this email.

        Best regards,
        The Kinah Team
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
                    <h1>Kinah</h1>
                    <p>Fast . Reliable . Easy</p>
                </div>
                <div class="content">
                    <h2>Hello {self.user.first_name},</h2>
                    <p>You've been invited to Kinahs or requested a password reset.</p>
                    <p>Click the button below to set your password:</p>
                    <a href="{reset_link}" class="button">Set Password</a>
                    <p>Or copy and paste this link into your browser:</p>
                    <p style="word-break: break-all; color: #667eea;">{reset_link}</p>
                    <p><strong>This link will expire in 15 minutes for security reasons.</strong></p>
                    <p>If you didn't request this, please ignore this email.</p>
                </div>
                <div class="footer">
                    <p>Best regards,<br>The Kinah Team</p>
                    <p>&copy; 2025 Kinah. All rights reserved.</p>
                </div>
            </div>
        </body>
        </html>
        """

        # Send the email using the helper function
        return self.send_email(subject, text_message, html_message)

    def send_email_verification_link(self, reset_link):
        """
        Send email verification link to user via email.
        """

        # Email subject
        subject = "Verify email"

        # Plain text message
        text_message = f"""
        Hello {self.user.first_name},

        Please proceed with your email verification process.
        
        Please click the link below to verify your email:
        {reset_link}

        This link will expire in 15 minutes for security reasons.

        If you didn't request this, please ignore this email.

        Best regards,
        The Kinah Team
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
                    <h1>Kinah</h1>
                    <p>Fast . Reliable . Easy</p>
                </div>
                <div class="content">
                    <h2>Hello {self.user.first_name},</h2>
                    <p>Please proceed with your email verification process.</p>
                    <p>Please click the link below to verify your email:</p>
                    <a href="{reset_link}" class="button">Set Password</a>
                    <p>Or copy and paste this link into your browser:</p>
                    <p style="word-break: break-all; color: #667eea;">{reset_link}</p>
                    <p><strong>This link will expire in 15 minutes for security reasons.</strong></p>
                    <p>If you didn't request this, please ignore this email.</p>
                </div>
                <div class="footer">
                    <p>Best regards,<br>The Kinah Team</p>
                    <p>&copy; 2025 Kinah. All rights reserved.</p>
                </div>
            </div>
        </body>
        </html>
        """

        # Send the email using the helper function
        return self.send_email(subject, text_message, html_message)

    def send_welcome_email(self):
        """
        Send welcome email when the account is created.
        """
        subject = "Welcome to Kinah's!"
        
        text_message = f"""
        Hello {self.user.first_name},

        Welcome to Kinas! Your account has been successfully created.

        You'll receive a separate email with instructions to verify your account.

        Best regards,
        The Kinahs Team
        """

        html_message = f"""
        <!DOCTYPE html>
        <html>
        <body style="font-family: Arial, sans-serif;">
            <div style="maxInlineSize: 600px; margin: 0 auto; padding: 20px;">
                <h2 style="color: #667eea;">Welcome to Mzansi Logistics!</h2>
                <p>Hello {self.user.first_name},</p>
                <p>Welcome to Mzansi Logistics! Your account has been successfully created.</p>
                <p>You'll receive a separate email with instructions to verify your account.</p>
                <p>Best regards,<br>The Kinahs Team</p>
            </div>
        </body>
        </html>
        """

        # Send the welcome email using the helper function
        return self.send_email(subject, text_message, html_message)
    
    def send_order_creation_email(self, order, order_link):
        # Email subject
        subject = "Your Kinah Order Has Been Created"

        # Plain text message
        text_message = f"""
        Hello {self.user.first_name},

        Your order has been successfully created on Kinah.

        Order No.: {order.order_number}
        Order Date: {order.created_at}

        You can view your order details using the link below:
        {order_link}

        Thank you for choosing Kinah.

        Best regards,
        The Kinah Team
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
                    max-width: 600px;
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
                .order-box {{
                    background: white;
                    padding: 15px;
                    border-radius: 6px;
                    margin: 20px 0;
                    border: 1px solid #eee;
                }}
                .footer {{
                    text-align: center;
                    margin-top: 20px;
                    color: #666;
                    font-size: 12px;
                }}
            </style>
        </head>
        <body>
            <div class="container">

                <div class="header">
                    <h1>Kinah</h1>
                    <p>Fast . Reliable . Easy</p>
                </div>

                <div class="content">

                    <h2>Hello {self.user.first_name},</h2>

                    <p>Your order has been successfully created on Kinah.</p>

                    <div class="order-box">
                        <p><strong>Order No.:</strong> {order.order_number}</p>
                        <p><strong>Order Date:</strong> {order.created_at}</p>
                    </div>

                    <p>You can view your order details by clicking the button below:</p>

                    <a href="{order_link}" class="button">View Order</a>

                    <p>Or copy and paste this link into your browser:</p>

                    <p style="word-break: break-all; color: #667eea;">
                        {order_link}
                    </p>

                    <p>We appreciate your business and will keep you updated on the progress of your order.</p>

                </div>

                <div class="footer">
                    <p>Best regards,<br>The Kinah Team</p>
                    <p>&copy; 2025 Kinah. All rights reserved.</p>
                </div>

            </div>
        </body>
        </html>
        """

        # Send email using the helper function
        return self.send_email(subject, text_message, html_message)

    def send_order_confirmation_email(self, order, order_link):
        # Subject email
        subject = f"Order Confirmation - #{order.order_number}"

        text_message = f"""
        Hello {self.user.first_name},

        Thank you for your order with Kinah!

        Order No.: {order.order_number}
        Order Date: {order.created_at}

        You can view your order details here:
        {order_link}

        Total Amount: ₦{order.total_amount}

        We will notify you once your order is shipped.

        Best regards,
        The Kinah Team
        """

        html_message = f"""
        <!DOCTYPE html>
        <html>
        <head>
        <meta charset="UTF-8">
        <style>

        body {{
            font-family: Arial, sans-serif;
            background-color: #f4f4f4;
            margin: 0;
            padding: 0;
        }}

        .container {{
            max-width: 600px;
            margin: auto;
            background: white;
        }}

        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 25px;
            text-align: center;
        }}

        .content {{
            padding: 25px;
        }}

        .order-box {{
            border: 1px solid #eee;
            padding: 15px;
            margin: 20px 0;
        }}

        .product-table {{
            width: 100%;
            border-collapse: collapse;
        }}

        .product-table th {{
            text-align: left;
            border-bottom: 1px solid #ddd;
            padding: 10px 0;
        }}

        .product-table td {{
            padding: 10px 0;
            border-bottom: 1px solid #f1f1f1;
        }}

        .button {{
            display: inline-block;
            background: #667eea;
            color: white;
            padding: 12px 25px;
            text-decoration: none;
            border-radius: 4px;
            margin-top: 20px;
        }}

        .footer {{
            text-align: center;
            padding: 20px;
            font-size: 12px;
            color: #777;
        }}

        </style>
        </head>

        <body>

        <div class="container">

        <div class="header">
        <h1>Kinah</h1>
        <p>Fast . Reliable . Easy</p>
        </div>

        <div class="content">

        <h2>Hello {self.user.first_name},</h2>

        <p>Thank you for your order! We're currently processing it.</p>

        <div class="order-box">

        <p><strong>Order No.:</strong> {order.order_number}</p>
        <p><strong>Order Date:</strong> {order.created_at}</p>
        <p><strong>Status:</strong> {order.status}</p>

        </div>

        <h3>Order Summary</h3>

        <table class="product-table">

        <tr>
        <th>Product</th>
        <th>Qty</th>
        <th>Price</th>
        </tr>

        {"".join([
        f'''
        <tr>
        <td>{item.product.name}</td>
        <td>{item.quantity}</td>
        <td>₦{item.price}</td>
        </tr>
        ''' for item in order.items.all()
        ])}

        </table>

        <h3>Total: ₦{order.total_amount}</h3>

        <h3>Shipping Address</h3>

        <p>
        {order.shipping_address.full_name}<br>
        {order.shipping_address.street_address}<br>
        {order.shipping_address.city}, {order.shipping_address.state}<br>
        {order.shipping_address.country}
        </p>

        <a href="{order_link}" class="button">View Order</a>

        <p style="margin-top:20px;">
        Or copy and paste this link into your browser:
        </p>

        <p style="word-break: break-all; color:#667eea;">
        {order_link}
        </p>

        </div>

        <div class="footer">

        <p>Best regards,<br>The Kinah Team</p>
        <p>© 2025 Kinah. All rights reserved.</p>

        </div>

        </div>

        </body>
        </html>
        """

        return self.send_email(subject, text_message, html_message)
    
    def send_order_cancel_pin(self, order, pin):
        subject = "Kinah Order Cancellation Code"

        text_message = f"""
        Hello,

        You requested to cancel your Kinah order.

        Order No.: {order.order_number}

        Your cancellation verification code is:

        {" ".join(pin)}

        This code will expire in 2 minutes.

        Enter this code on the cancellation page to confirm your request.

        If you did not request this cancellation, please ignore this email and your order will remain unchanged.

        Best regards,
        The Kinah Team
        """

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
            max-width: 600px;
            margin: auto;
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

        .pin-box {{
            background: white;
            border: 1px solid #ddd;
            padding: 20px;
            text-align: center;
            font-size: 28px;
            font-weight: bold;
            letter-spacing: 6px;
            color: #667eea;
            margin: 25px 0;
            border-radius: 6px;
        }}

        .order-box {{
            background: white;
            border: 1px solid #eee;
            padding: 15px;
            border-radius: 6px;
            margin: 20px 0;
        }}

        .footer {{
            text-align: center;
            margin-top: 20px;
            color: #777;
            font-size: 12px;
        }}

        </style>
        </head>

        <body>

        <div class="container">

        <div class="header">
        <h1>Kinah</h1>
        <p>Fast . Reliable . Easy</p>
        </div>

        <div class="content">

        <h2>Order Cancellation Verification</h2>

        <p>You requested to cancel an order on Kinah.</p>

        <div class="order-box">
        <p><strong>Order No:</strong> {order.order_number}</p>
        </div>

        <p>Please use the verification code below to confirm your cancellation request:</p>

        <div class="pin-box">
        {" ".join(pin)}
        </div>

        <p><strong>This code will expire in 2 minutes.</strong></p>

        <p>Enter this code on the cancellation page to complete the request.</p>

        <p>If you did not request this cancellation, you can safely ignore this email and your order will remain unchanged.</p>

        </div>

        <div class="footer">

        <p>Best regards,<br>The Kinah Team</p>

        <p>&copy; 2025 Kinah. All rights reserved.</p>

        </div>

        </div>

        </body>
        </html>
        """

        return self.send_email(subject, text_message, html_message)

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


class DecimalDatetimeUUIDEncoder(json.JSONEncoder):
    '''
    Class to parse Decimal, UUID, Datetime, Set object in test
    '''
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        if isinstance(obj, uuid.UUID) or isinstance(obj, datetime):
            return str(obj)
        if isinstance(obj, set):
            return list(obj)
        return super().default(obj)
    
def printInJSON(data):
    '''
    Helper function to print dict response to console in json
    '''
    print(json.dumps(data, indent=3, cls=DecimalDatetimeUUIDEncoder))