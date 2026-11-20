from celery import Celery
from database import settings

celery_app = Celery(
    "warehouse_inventory",
    broker=settings.CELERY_BROKER_URL,
    include=["tasks.inventory_notification"],
)