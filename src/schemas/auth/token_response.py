"""Schema for authentication token responses."""

from pydantic import BaseModel


class TokenResponse(BaseModel):
    """Response schema for authentication tokens.

    Attributes:
        access_token (str): Short-lived JWT for API authorization.
        refresh_token (str): Long-lived JWT for obtaining new access tokens.
        token_type (str): Always 'bearer'.
    """

    access_token: str
    refresh_token: str
    token_type: str = "bearer"
