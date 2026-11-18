import logging
import time

logger = logging.getLogger("uvicorn.error")


def simulate_welcome_email(email: str) -> None:
    # Simulate a slow email service
    time.sleep(3)

    logger.info(
        "SIMULATED welcome email sent to %s: \n"
        "Welcome to the Warehouse Management System!",
        email,
    )