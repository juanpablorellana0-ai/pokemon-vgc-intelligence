"""Structured logger for Showdown sync events.

Emits one line per event with a stable ``event`` key so future log
aggregation can filter reliably.
"""
from __future__ import annotations
import json
import logging
from typing import Any

_logger = logging.getLogger("showdown.sync")

# Event names required by the spec — exposed as constants so callers
# cannot mistype them silently.
EVT_STARTED = "SHOWDOWN_SYNC_STARTED"
EVT_UPDATE_AVAILABLE = "SHOWDOWN_UPDATE_AVAILABLE"
EVT_UP_TO_DATE = "SHOWDOWN_UP_TO_DATE"
EVT_IMPORT_STARTED = "SHOWDOWN_IMPORT_STARTED"
EVT_VALIDATION_STARTED = "SHOWDOWN_VALIDATION_STARTED"
EVT_VALIDATION_FAILED = "SHOWDOWN_VALIDATION_FAILED"
EVT_TESTS_STARTED = "SHOWDOWN_TESTS_STARTED"
EVT_TESTS_FAILED = "SHOWDOWN_TESTS_FAILED"
EVT_VERSION_ACTIVATED = "SHOWDOWN_VERSION_ACTIVATED"
EVT_ROLLBACK_STARTED = "SHOWDOWN_ROLLBACK_STARTED"
EVT_ROLLBACK_COMPLETED = "SHOWDOWN_ROLLBACK_COMPLETED"
EVT_LOCKED = "SHOWDOWN_SYNC_LOCKED"
EVT_ERROR = "SHOWDOWN_SYNC_ERROR"


def log(event: str, **fields: Any) -> None:
    payload = {"event": event, **fields}
    _logger.info(json.dumps(payload, default=str, ensure_ascii=False))
