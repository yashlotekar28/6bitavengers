"""
Celery application factory.
Broker & result backend both use Redis.
Person A — Backend/Integration
"""
import os
from celery import Celery

CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0")
CELERY_RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND", "redis://localhost:6379/0")

celery = Celery(
    "nirikshan",
    broker=CELERY_BROKER_URL,
    backend=CELERY_RESULT_BACKEND,
    include=["app.tasks.verification_tasks"],
)

celery.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="Asia/Kolkata",
    enable_utc=True,
    task_track_started=True,
    task_acks_late=True,                # Ensure tasks survive worker crashes
    worker_prefetch_multiplier=1,       # One task at a time per worker (verification is I/O heavy)
    result_expires=3600,                # Results stored for 1 hour
)
