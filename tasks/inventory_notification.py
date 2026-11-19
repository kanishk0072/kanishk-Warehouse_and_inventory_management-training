import time
from celery.utils.log import get_task_logger
from celery_app import celery_app

logger = get_task_logger(__name__)


@celery_app.task(name="tasks.notify_inventory_team")
def notify_inventory_team(sku: str):
    time.sleep(3)
    logger.info("Inventory team notified for SKU: %s", sku)