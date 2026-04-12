"""Shared base fields for menu item request and response schemas."""

from abc import ABC

from pydantic import BaseModel, Field


class MenuItemBase(BaseModel, ABC):
    """Abstract base with shared menu item fields.

    Attributes:
        name (str): Display name of the menu item.
        price (float): Price of the menu item in shekels.
    """

    name: str = Field(min_length=1, max_length=100)
    price: float = Field(gt=0)
