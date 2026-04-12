"""Counter MongoDB document model."""

from beanie import Document


class CounterDocument(Document):
    """MongoDB document model for auto-incrementing counters.

    Attributes:
        sequence_value (int): The current counter value. Defaults to 0.
    """

    sequence_value: int = 0

    class Settings:
        """Beanie document configuration."""

        name = "counters"
