import os
from celery import Celery
from celery.schedules import crontab

# Set default Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mzansi_logistics.settings')

# Create Celery app
app = Celery('mzansi_logistics')

# Load config from Django settings with CELERY namespace
app.config_from_object('django.conf:settings', namespace='CELERY')

# Auto-discover tasks in all installed apps
app.autodiscover_tasks()

# Configure periodic tasks
app.conf.beat_schedule = {
    'update-receivables-daily': {
        'task': 'finance.tasks.update_receivables_task',
        'schedule': crontab(hour=0, minute=0),  # Run daily at midnight
    },
    'process-scheduled-sms': {
        'task': 'communications.tasks.process_scheduled_sms_task',
        'schedule': crontab(minute='*/5'),  # Run every 5 minutes
    },
}

@app.task(bind=True, ignore_result=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
