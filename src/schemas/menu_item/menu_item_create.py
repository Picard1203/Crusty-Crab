"""Schema for menu item creation requests."""

from src.schemas.base_request import BaseRequest
from src.schemas.menu_item.menu_item_base import MenuItemBase


class MenuItemCreate(MenuItemBase, BaseRequest):
    """Request schema for creating a new Krusty Crab menu item."""
