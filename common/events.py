"""
Shared event types and schemas for inter-service communication via RabbitMQ.
"""

from datetime import datetime, timezone
from enum import Enum
import json


# ── Event Types ──────────────────────────────────────────────

class EventType(str, Enum):
    JOB_CLICKED = "job_clicked"
    JOB_APPLIED = "job_applied"
    JOB_SEARCHED = "job_searched"
    USER_REGISTERED = "user_registered"
    USER_UPDATED = "user_updated"
    RECO_INVALIDATE = "reco_invalidate"


# ── Queue Names ──────────────────────────────────────────────

class Queue:
    USER_ACTIVITY = "user.activity"
    RECO_INVALIDATE = "reco.invalidate"


# ── Exchange Names ───────────────────────────────────────────

class Exchange:
    EVENTS = "jrs.events"


# ── Event Builder ────────────────────────────────────────────

def build_event(event_type: EventType, user_id: str, data: dict = None) -> str:
    """Build a JSON-serialized event message."""
    event = {
        "event_type": event_type.value,
        "user_id": user_id,
        "data": data or {},
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    return json.dumps(event)


def parse_event(body: bytes) -> dict:
    """Parse a raw RabbitMQ message body into an event dict."""
    return json.loads(body.decode("utf-8"))
