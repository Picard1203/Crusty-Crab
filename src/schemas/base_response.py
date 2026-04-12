"""Base response schema for all outgoing API responses."""

from abc import ABC
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class BaseResponse(BaseModel, ABC):
    """Abstract base class for all response schemas.

    Attributes:
        created_at (datetime): When the entity was created.
    """

    model_config = ConfigDict(from_attributes=True)
    created_at: datetime
