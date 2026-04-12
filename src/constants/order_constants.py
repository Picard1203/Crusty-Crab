"""Order lifecycle constants including allowed status transitions."""

from typing import List, Tuple

WORKER_ALLOWED_TRANSITIONS: List[Tuple[str, str]] = [
    ("order_received", "order_confirmed"),
    ("order_confirmed", "order_being_prepared"),
    ("order_being_prepared", "order_ready"),
    ("order_ready", "order_complete"),
    ("order_received", "order_cancelled"),
    ("order_confirmed", "order_cancelled"),
    ("order_being_prepared", "order_cancelled"),
]
