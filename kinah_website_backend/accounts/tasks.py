from celery import shared_task
from django.contrib.auth import get_user_model

from .utils import EmailService


User = get_user_model()

@shared_task
def send_welcome_email_task(user_id):
    user = User.objects.get(id=user_id)
    email_service = EmailService(user.email, user=user)
    email_service.send_welcome_email()

@shared_task
def send_email_verification_task(user_id, verification_link):
    user = User.objects.get(id=user_id)
    email_service = EmailService(user.email, user=user)
    email_service.send_email_verification_link(verification_link)

@shared_task
def send_password_reset_link_task(user_id, reset_link, password=None):
    user = User.objects.get(id=user_id)
    email_service = EmailService(user.email, user=user)
    email_service.send_password_reset_link(reset_link, password)

@shared_task
def send_user_verification_otp_task(user_id, pin):
    if user_id is None:
        return
    try:
        user = User.objects.get(id=user_id)
        email_service = EmailService(user.email, user=user)
        email_service.send_user_otp(pin)
    except Exception as e:
        return

