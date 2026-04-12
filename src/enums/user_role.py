"""User role enumeration for the Krusty Crab permission system."""

from enum import Enum


class UserRole(str, Enum):
    """Represents all permission levels available in the system.

    Attributes:
        GUEST: A customer who can place and view their own orders.
        WORKER: A staff member who can update order statuses.
        ADMINISTRATOR: A manager with full system access.
    """

    GUEST = "guest"
    WORKER = "worker"
    ADMINISTRATOR = "administrator"
