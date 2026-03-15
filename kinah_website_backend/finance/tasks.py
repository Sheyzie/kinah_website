from celery import shared_task
from accounts.utils import EmailService
from .models import WebhookEvent, Order
from .payment_service import process_successful_payment, process_failed_webhook
import logging
logger = logging.getLogger(__name__)

@shared_task
def process_webhook_event(webhook_id=None):
    logger.info("Processing paystack webhook event")

    if not webhook_id:
        process_failed_webhook()

    try:
        webhook = WebhookEvent.objects.get(id=webhook_id)

        if not webhook.processed:
            process_failed_webhook()

        payload = webhook.payload
        event = webhook.event_type

        if event == "charge.success":
            process_successful_payment(payload)

        webhook.processed = True
        webhook.save()
    except Exception as e:
        return
    
@shared_task
def send_order_creation_email_task(order_id=None, order_link=None):
    if order_id is None:
        return
    try:
        order = Order.objects.get(id=order_id)
        email_service = EmailService(order.customer_email)
        email_service.send_order_creation_email(order, order_link)
    except Exception as e:
        return

@shared_task
def send_order_confirmation_email_task(order_id=None, order_link=None):
    if order_id is None:
        return
    try:
        order = Order.objects.get(id=order_id)
        email_service = EmailService(order.customer_email)
        email_service.send_order_confirmation_email(order, order_link)
    except Exception as e:
        return
    
@shared_task
def send_order_cancel_pin_task(order_id=None, pin=None):
    if order_id is None:
        return
    try:
        order = Order.objects.get(id=order_id)
        email_service = EmailService(order.customer_email)
        email_service.send_order_cancel_pin(order, pin)
    except Exception as e:
        return

