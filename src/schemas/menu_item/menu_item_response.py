"""Schema for menu item response payloads."""

from datetime import datetime

from src.schemas.base_response import BaseResponse
from src.schemas.menu_item.menu_item_base import MenuItemBase


class MenuItemResponse(MenuItemBase, BaseResponse):
    """Response schema for a Krusty Crab menu item.

    Attributes:
        item_number (int): The auto-assigned menu item identifier.
        is_active (bool): Whether the item is available for ordering.
        updated_at (datetime): When the menu item was last modified.
    """

    item_number: int
    is_active: bool
    updated_at: datetime
