"""Base request schema for all incoming API requests."""

from abc import ABC

from pydantic import BaseModel


class BaseRequest(BaseModel, ABC):
    """Abstract base class for all request schemas."""
