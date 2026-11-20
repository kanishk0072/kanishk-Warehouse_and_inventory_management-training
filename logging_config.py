import logging
import sys
from contextvars import ContextVar

from pythonjsonlogger.json import JsonFormatter


request_id_ctx = ContextVar("request_id", default="-")


class RequestIdFilter(logging.Filter):
    def filter(self, record):
        record.request_id = request_id_ctx.get()
        return True


def configure_logging():
    handler = logging.StreamHandler(sys.stdout)

    handler.setFormatter(
        JsonFormatter(
            "%(asctime)s %(levelname)s %(name)s %(message)s %(request_id)s"
        )
    )

    handler.addFilter(RequestIdFilter())

    for name in ("", "uvicorn.error", "uvicorn.access"):
        logger = logging.getLogger(name)
        logger.handlers = [handler]
        logger.setLevel(logging.INFO)
        logger.propagate = False