import logging
import time

logger = logging.getLogger("uvicorn.error")


def notify_inventory_team(sku: str):
    time.sleep(2)

    logger.info(
        "INVENTORY NOTIFICATION: "
        "New product with SKU %s has been created. "
        "Please verify warehouse stock availability.",
        sku,
    )