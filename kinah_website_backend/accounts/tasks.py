from celery import shared_task
from django.contrib.auth import get_user_model

from .utils import send_password_reset_link, send_welcome_email,send_email_verification_link


User = get_user_model()

@shared_task
def send_welcome_email_task(user_id):
    user = User.objects.get(id=user_id)
    send_welcome_email(user)

@shared_task
def send_email_verification_task(user_id, reset_link):
    user = User.objects.get(id=user_id)
    send_email_verification_link(user, reset_link)

@shared_task
def send_password_reset_link_task(user_id, reset_link, password=None):
    user = User.objects.get(id=user_id)
    send_password_reset_link(user, reset_link, password)

