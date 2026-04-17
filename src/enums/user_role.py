"""User role enumeration for the Krusty Crab permission system."""

from enum import Enum


class UserRole(str, Enum):
    """Represents all permission levels available in the system."""

    GUEST = "guest"
    WORKER = "worker"
    ADMINISTRATOR = "administrator"
