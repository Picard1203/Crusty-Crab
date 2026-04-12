"""Paginated response wrapper for list endpoints."""

from typing import Generic, List, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")


class PaginatedResponse(BaseModel, Generic[T]):
    """Paginated wrapper for list endpoint responses.

    Attributes:
        items (List[T]): The page of results.
        total (int): Total matching entities across all pages.
        skip (int): Number of entities skipped.
        limit (int): Maximum entities per page.
        has_more (bool): Whether more pages exist after this one.
    """

    items: List[T]
    total: int = Field(ge=0)
    skip: int = Field(ge=0, default=0)
    limit: int = Field(ge=1, default=10)
    has_more: bool
