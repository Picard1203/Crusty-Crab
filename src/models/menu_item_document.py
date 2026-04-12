"""Menu item MongoDB document model."""

from datetime import datetime, timezone

from beanie import Indexed
from pydantic import Field

from src.models.base_document import BaseDocument


class MenuItemDocument(BaseDocument):
    """MongoDB document model for a Krusty Crab menu item.

    Attributes:
        item_number (int): Unique auto-increment menu item identifier.
        name (str): The display name of the menu item. Must be unique.
        price (float): The price of the menu item in shekels.
        is_active (bool): Whether the item is available for ordering.
            Defaults to True.
        updated_at (datetime): Timestamp of the last update.
            Defaults to current UTC time.
    """

    item_number: Indexed(int, unique=True)  # type: ignore
    name: Indexed(str, unique=True)  # type: ignore
    price: float = Field(gt=0)
    is_active: bool = True
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    class Settings:
        """Beanie document configuration."""

        name = "menu_items"
