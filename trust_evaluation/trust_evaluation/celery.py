import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'trust_evaluation.settings')

app = Celery('trust_evaluation')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()