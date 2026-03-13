from celery import shared_task
from .models import WebhookEvent
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