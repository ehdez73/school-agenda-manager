import logging
import os
import uuid
from typing import Any

from flask import g, has_request_context, request


def _get_level_from_env() -> int:
    level_name = os.getenv("BACKEND_LOG_LEVEL", "INFO").upper()
    return getattr(logging, level_name, logging.INFO)


def setup_logging() -> None:
    """Configure root logging once for the backend process."""
    if getattr(setup_logging, "_configured", False):
        return

    root_logger = logging.getLogger()
    root_logger.setLevel(_get_level_from_env())

    handler = logging.StreamHandler()
    formatter = logging.Formatter(
        "%(asctime)s %(levelname)s [%(name)s] request_id=%(request_id)s task_id=%(task_id)s %(message)s",
        defaults={"request_id": "-", "task_id": "-"},
    )
    handler.setFormatter(formatter)

    root_logger.handlers.clear()
    root_logger.addHandler(handler)

    werkzeug_logger = logging.getLogger("werkzeug")
    werkzeug_logger.setLevel(logging.ERROR)
    werkzeug_logger.propagate = False

    setup_logging._configured = True


def get_request_id() -> str:
    """Return the request id from context, or generate one when available."""
    if not has_request_context():
        return "-"

    req_id = getattr(g, "request_id", None)
    if req_id:
        return req_id

    incoming = request.headers.get("X-Request-ID")
    req_id = incoming or str(uuid.uuid4())
    g.request_id = req_id
    return req_id


def build_log_extra(task_id: str | None = None) -> dict[str, Any]:
    """Build contextual extra fields used by log formatter."""
    extra = {"request_id": get_request_id(), "task_id": "-"}
    if task_id:
        extra["task_id"] = task_id
    return extra
