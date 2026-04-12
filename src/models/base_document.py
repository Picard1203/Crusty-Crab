"""Base document model providing shared fields for all entities."""

from datetime import datetime, timezone

from beanie import Document
from pydantic import Field


class BaseDocument(Document):
    """Base class for all MongoDB document models.

    Attributes:
        created_at (datetime): The timestamp when the document was created.
            Defaults to the current UTC time.
    """

    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    class Settings:
        """Beanie document configuration."""
