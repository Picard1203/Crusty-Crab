"""Unit tests for TokenHandler."""

from typing import Any, Dict

import pytest

from src.auth.token_handler import TokenHandler
from src.exceptions import AuthenticationException


class TestTokenHandler:
    """Test suite for JWT token creation and validation workflows."""

    def test_create_access_token(self, token_handler: TokenHandler) -> None:
        """Generated access token is a valid non-empty string.

        Args:
            token_handler (TokenHandler): The token handler.
        """
        token: str = token_handler.create_access_token({"sub": "testuser"})
        assert isinstance(token, str)
        assert len(token) > 0

    def test_decode_access_token(self, token_handler: TokenHandler) -> None:
        """Access token decodes to expected subject and type.

        Args:
            token_handler (TokenHandler): The token handler.
        """
        token: str = token_handler.create_access_token({"sub": "testuser"})
        payload: Dict[str, Any] = token_handler.decode_token(
            token, expected_type="access"
        )
        assert payload["sub"] == "testuser"
        assert payload["type"] == "access"

    def test_create_and_decode_refresh_token(
        self, token_handler: TokenHandler
    ) -> None:
        """Refresh token preserves claims and correct type through round-trip.

        Args:
            token_handler (TokenHandler): The token handler.
        """
        token: str = token_handler.create_refresh_token({"sub": "testuser"})
        payload: Dict[str, Any] = token_handler.decode_token(
            token, expected_type="refresh"
        )
        assert payload["sub"] == "testuser"
        assert payload["type"] == "refresh"

    def test_decode_wrong_type_raises(
        self, token_handler: TokenHandler
    ) -> None:
        """Mismatching token type raises AuthenticationException.

        Args:
            token_handler (TokenHandler): The token handler.
        """
        token: str = token_handler.create_access_token({"sub": "testuser"})
        with pytest.raises(AuthenticationException):
            token_handler.decode_token(token, expected_type="refresh")

    def test_decode_invalid_token_raises(
        self, token_handler: TokenHandler
    ) -> None:
        """Malformed token string raises AuthenticationException.

        Args:
            token_handler (TokenHandler): The token handler.
        """
        with pytest.raises(AuthenticationException):
            token_handler.decode_token("not.a.valid.token")
