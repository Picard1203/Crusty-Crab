"""Schema for a single-value statistics response."""

from typing import Optional

from pydantic import BaseModel


class StatisticsResponse(BaseModel):
    """Generic response schema for a single aggregated statistic.

    Attributes:
        value (float): The numeric statistic value.
        label (Optional[str]): Optional label (e.g., item name).
    """

    value: float
    label: Optional[str] = None
