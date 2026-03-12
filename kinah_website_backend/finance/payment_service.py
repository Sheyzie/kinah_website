from django.urls import reverse
from django.conf import settings
from django.utils.dateparse import parse_datetime
from django.db import transaction
from typing import Any
import requests
import hashlib
import hmac
import uuid

from .models import Order, Payment, WebhookEvent

import logging
logger = logging.getLogger(__name__)


PAYSTACK_SECRET_KEY = getattr(settings, 'PAYSTACK_SECRET_KEY', None)


class PaystackInit:
    
    def __init__(self):
        self.url = "https://api.paystack.co/transaction/initialize"
        self.headers = None
        if PAYSTACK_SECRET_KEY is not None:
            self.headers = {
                "Authorization": f"Bearer {PAYSTACK_SECRET_KEY}"
            }

    def list_transactions(self):
        success = False
        message = ""
        data = None
        url = "https://api.paystack.co/transaction"

        if self.headers is None:
            message = 'Error getting transactions'
            return (success, message, data)

        try:
            response = requests.get(url, headers=self.headers)
            response_data = response.json()

            if response.status_code != 200:
                message = 'Unable to get transactions for paystack'
                return (success, message, data)
            
            success = True
            data = response_data['data']
            message = 'Paystack transactions retrieved successfully'
            return (success, message, data)
        except requests.exceptions.RequestException as e:
            return (False, str(e), None)
    
    def get_transaction(self, transaction_id):
        success = False
        message = ""
        data = None
        url = f"https://api.paystack.co/transaction/{transaction_id}"

        if self.headers is None:
            message = f'Error getting transaction with {transaction_id}'
            return (success, message, data)

        try:
            response = requests.get(url, headers=self.headers, timeout=10)
        
            response_data = response.json()

            if response.status_code != 200:
                message = f'Unable to get transactions for paystack with {transaction_id}'
                return (success, message, data)
            
            success = True
            data = response_data['data']
            message = 'Paystack transaction retrieved successfully'
            return (success, message, data)
        except requests.exceptions.RequestException as e:
            return (False, str(e), None)

    def initialize(self, email: str, amount: int, order_id: str):
        success = False
        message = ""
        data = None
        if not email or amount is None:
            message = "Email and Amount are required"
            return (success, message, data)
        
        payload = {
            "email": email,
            "amount": amount * 100,
            "channels": [
                "card", "bank", "apple_pay", 
                "ussd", "bank_transfer"
            ],
            "currency": "NGN",
            "callback_url": 'https://manually-indictable-angelika.ngrok-free.dev/api/v1/paystack/webhook/',
            # "callback_url": reverse('paystack-webhook'),
            # "reference": str(uuid.uuid4())
            "reference": order_id
        }

        if self.headers is None:
            message = 'Error initializing paystack'
            return (success, message, data)

        try:
            response = requests.post(self.url, json=payload, headers=self.headers)
            response_data = response.json()

            if response.status_code != 200:
                message = 'Paystack initialization failed'
                return (success, message, data)
            
            success = True
            data = response_data['data']
            message = 'Paystack initialization successful'
            return (success, message, data)
        except requests.exceptions.RequestException as e:
            return (False, str(e), None)

    def verify(self, reference: str):
        success = False
        message = ""
        data = None
        url = f"https://api.paystack.co/transaction/verify/{reference}"

        if self.headers is None:
            message = f'Error verifying paystack transaction with {reference}'
            return (success, message, data)
        
        try:
            response = requests.get(url, headers=self.headers)
            response_data = response.json()

            if response.status_code != 200:
                message = 'Paystack transaction verification failed'
                return (success, message, data)
            
            success = True
            data = response_data['data']
            message = 'Paystack verification successful'
            return (success, message, data)
        except requests.exceptions.RequestException as e:
            return (False, str(e), None)
        
    def verify_signature(self, request):
        '''
        To verify Paystack webhook sgnature
        '''
        signature = request.headers.get("x-paystack-signature")

        computed_hash = hmac.new(
            PAYSTACK_SECRET_KEY.encode(),
            request.body,
            hashlib.sha512
        ).hexdigest()

        return signature == computed_hash
    
    def is_paystack_valid_ip(self, request):
        allowed_ips = settings.PAYSTACK_WEBHOOK_IPS

        ip = request.META.get("HTTP_X_FORWARDED_FOR")

        if ip:
            ip = ip.split(",")[0]
        else:
            ip = request.META.get("REMOTE_ADDR")

        return ip in allowed_ips

@transaction.atomic
def process_successful_payment(payload: dict[str, Any]):
    logger.info("Processing successful payment", extra=payload)

    data = payload.get("data", {})
    payment_data = {
        'reference': data.get('reference'),
        'amount': data.get('amount'),
        'status': 'completed' if data.get('status') == 'success' else 'failed',
        'transaction_id': data.get('id'),
        'payment_method': data.get('channel'),
        'paid_at': data.get('paid_at'),
        'currency': data.get('currency'),
        'ip_address': data.get('ip_address'),
        # 'customer': data.get('customer),
        'gateway_response': payload
    }

    if not payment_data:
        return
    
    payment_exists = Payment.objects.filter(
        transaction_id=payment_data["transaction_id"]
    ).exists()

    if payment_exists:
        return
    
    reference = payment_data.pop('reference', None)
    paid_at = parse_datetime(payment_data.pop('paid_at'))
    currency = payment_data.pop('currency', None)
    ip_address = payment_data.pop('ip_address')
    try:
        order = Order.objects.get(id=reference)
        order.paid_at = paid_at
        # order.currency = currency
        order.ip_address = ip_address
        order.status = 'confirmed'
        order.save()
        payment = Payment.objects.create(
            order=order,
            **payment_data
        )
        print('PROCESSED')
    except Exception as e:
        # TODO: Create a model to hold failed payment process
        return

@transaction.atomic
def process_failed_webhook():
    logger.info("Processing failed webhook")

    webhooks = WebhookEvent.objects.filter(processed=False)

    for webhook in webhooks:
        payload = webhook.payload

        data = payload.get("data", {})
        payment_data = {
            'reference': data.get('reference'),
            'amount': data.get('amount'),
            'status': 'completed' if data.get('status') == 'success' else 'failed',
            'transaction_id': data.get('id'),
            'payment_method': data.get('channel'),
            'paid_at': data.get('paid_at'),
            'currency': data.get('currency'),
            'ip_address': data.get('ip_address'),
            # 'customer': data.get('customer),
            'gateway_response': payload
        }
    
        payment_exists = Payment.objects.filter(
            transaction_id=payment_data["transaction_id"]
        ).exists()

        if payment_exists:
            return
    
        reference = payment_data.pop('reference', None)
        paid_at = parse_datetime(payment_data.pop('paid_at'))
        currency = payment_data.pop('currency', None)
        ip_address = payment_data.pop('ip_address')
        try:
            order = Order.objects.get(id=reference)
            order.paid_at = paid_at
            # order.currency = currency
            order.ip_address = ip_address
            order.save()
            payment = Payment.objects.create(
                order=order,
                **payment_data
            )
            print('PROCESSED')
        except Exception as e:
            # TODO: Create a model to hold failed payment process
            return
        
        webhook.processed = True
        webhook.save()




# -----------------
# Initialize response
# -----------------

# {
#   "status": true,
#   "message": "Authorization URL created",
#   "data": {
#     "authorization_url": "https://checkout.paystack.com/3ni8kdavz62431k",
#     "access_code": "3ni8kdavz62431k",
#     "reference": "re4lyvq3s3"
#   }
# }


# -----------------
# Verify response
# -----------------

# {
#   "status": true,
#   "message": "Verification successful",
#   "data": {
#     "id": 4099260516,
#     "domain": "test",
#     "status": "success",
#     "reference": "re4lyvq3s3",
#     "receipt_number": null,
#     "amount": 40333,
#     "message": null,
#     "gateway_response": "Successful",
#     "paid_at": "2024-08-22T09:15:02.000Z",
#     "created_at": "2024-08-22T09:14:24.000Z",
#     "channel": "card",
#     "currency": "NGN",
#     "ip_address": "197.210.54.33",
#     "metadata": "",
#     "log": {
#       "start_time": 1724318098,
#       "time_spent": 4,
#       "attempts": 1,
#       "errors": 0,
#       "success": true,
#       "mobile": false,
#       "input": [],
#       "history": [
#         {
#           "type": "action",
#           "message": "Attempted to pay with card",
#           "time": 3
#         },
#         {
#           "type": "success",
#           "message": "Successfully paid with card",
#           "time": 4
#         }
#       ]
#     },
#     "fees": 10283,
#     "fees_split": null,
#     "authorization": {
#       "authorization_code": "AUTH_uh8bcl3zbn",
#       "bin": "408408",
#       "last4": "4081",
#       "exp_month": "12",
#       "exp_year": "2030",
#       "channel": "card",
#       "card_type": "visa ",
#       "bank": "TEST BANK",
#       "country_code": "NG",
#       "brand": "visa",
#       "reusable": true,
#       "signature": "SIG_yEXu7dLBeqG0kU7g95Ke",
#       "account_name": null
#     },
#     "customer": {
#       "id": 181873746,
#       "first_name": null,
#       "last_name": null,
#       "email": "demo@test.com",
#       "customer_code": "CUS_1rkzaqsv4rrhqo6",
#       "phone": null,
#       "metadata": null,
#       "risk_action": "default",
#       "international_format_phone": null
#     },
#     "plan": null,
#     "split": {},
#     "order_id": null,
#     "paidAt": "2024-08-22T09:15:02.000Z",
#     "createdAt": "2024-08-22T09:14:24.000Z",
#     "requested_amount": 30050,
#     "pos_transaction_data": null,
#     "source": null,
#     "fees_breakdown": null,
#     "connect": null,
#     "transaction_date": "2024-08-22T09:14:24.000Z",
#     "plan_object": {},
#     "subaccount": {}
#   }
# }


# -----------------
# Transaction response
# -----------------

# {
#   "event": "charge.success",
#   "data": {
#     "id": 302961,
#     "domain": "live",
#     "status": "success",
#     "reference": "qTPrJoy9Bx",
#     "amount": 10000,
#     "message": null,
#     "gateway_response": "Approved by Financial Institution",
#     "paid_at": "2016-09-30T21:10:19.000Z",
#     "created_at": "2016-09-30T21:09:56.000Z",
#     "channel": "card",
#     "currency": "NGN",
#     "ip_address": "41.242.49.37",
#     "metadata": 0,
#     "log": {
#       "time_spent": 16,
#       "attempts": 1,
#       "authentication": "pin",
#       "errors": 0,
#       "success": false,
#       "mobile": false,
#       "input": [],
#       "channel": null,
#       "history": [
#         {
#           "type": "input",
#           "message": "Filled these fields: card number, card expiry, card cvv",
#           "time": 15
#         },
#         {
#           "type": "action",
#           "message": "Attempted to pay",
#           "time": 15
#         },
#         {
#           "type": "auth",
#           "message": "Authentication Required: pin",
#           "time": 16
#         }
#       ]
#     },
#     "fees": null,
#     "customer": {
#       "id": 68324,
#       "first_name": "BoJack",
#       "last_name": "Horseman",
#       "email": "bojack@horseman.com",
#       "customer_code": "CUS_qo38as2hpsgk2r0",
#       "phone": null,
#       "metadata": null,
#       "risk_action": "default"
#     },
#     "authorization": {
#       "authorization_code": "AUTH_f5rnfq9p",
#       "bin": "539999",
#       "last4": "8877",
#       "exp_month": "08",
#       "exp_year": "2020",
#       "card_type": "mastercard DEBIT",
#       "bank": "Guaranty Trust Bank",
#       "country_code": "NG",
#       "brand": "mastercard",
#       "account_name": "BoJack Horseman"
#     },
#     "plan": {}
#   }
# }


# curl https://manually-indictable-angelika.ngrok-free.dev/api/v1/payments/ -H "Authorization: Bearer sk_test_0cbd63c11a0f48cce42cf29d9356ef95ec972947" -H "Content-Type: application/json" -d "'{"email": "customer@mail.com", "amount": "2000"}'" -X POST
