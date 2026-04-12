"""Schema for token refresh requests."""

from src.schemas.base_request import BaseRequest


class TokenRefreshRequest(BaseRequest):
    """Request schema for exchanging a refresh token.

    Attributes:
        refresh_token (str): The valid refresh JWT to exchange.
    """

    refresh_token: str
