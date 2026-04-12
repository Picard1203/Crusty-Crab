"""Shared base fields for order request and response schemas."""

from abc import ABC
from typing import List

from pydantic import BaseModel, Field, field_validator


class OrderBase(BaseModel, ABC):
    """Abstract base with shared order fields.

    Attributes:
        orderer_name (str): The name of the customer placing the order.
        items (List[str]): Names of menu items being ordered.
    """

    orderer_name: str = Field(min_length=1, max_length=100)
    items: List[str] = Field(min_length=1)

    @field_validator("orderer_name", mode="before")
    @classmethod
    def strip_whitespace(cls, value: object) -> object:
        """Strip leading/trailing whitespace from orderer name.

        Args:
            value (object): The raw input value.

        Returns:
            object: Trimmed string if input was a string, otherwise unchanged.
        """
        if isinstance(value, str) is True:
            return value.strip()
        return value
