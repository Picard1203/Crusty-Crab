"""JWT token creation and validation."""

import logging
from datetime import datetime, timedelta, timezone
from typing import Dict

from jose import JWTError, jwt

from src.constants.auth_constants import (
    ACCESS_TOKEN_TYPE,
    JWT_EXP_CLAIM,
    JWT_SUB_CLAIM,
    JWT_TYPE_CLAIM,
    REFRESH_TOKEN_TYPE,
)
from src.exceptions import AuthenticationError
from src.settings import Settings

logger = logging.getLogger(__name__)


class TokenHandler:
    """Creates and validates JWT access and refresh tokens.

    Attributes:
        _settings (Settings): Application settings for JWT configuration.
    """

    def __init__(self, settings: Settings) -> None:
        """Initialize with application settings.

        Args:
            settings (Settings): Settings containing JWT secret, algorithm,
                and expiration configuration.
        """
        self._settings: Settings = settings

    def create_access_token(self, data: Dict[str, str]) -> str:
        """Create a short-lived JWT access token.

        Args:
            data (Dict[str, str]): Claims to encode (typically {"sub": username}).

        Returns:
            str: The encoded JWT string.
        """
        to_encode = data.copy()
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=self._settings.access_token_expire_minutes
        )
        to_encode[JWT_EXP_CLAIM] = expire
        to_encode[JWT_TYPE_CLAIM] = ACCESS_TOKEN_TYPE
        logger.debug(f"Creating access token for {data.get(JWT_SUB_CLAIM)}")
        return jwt.encode(
            to_encode,
            self._settings.jwt_secret,
            algorithm=self._settings.jwt_algorithm,
        )

    def create_refresh_token(self, data: Dict[str, str]) -> str:
        """Create a long-lived JWT refresh token.

        Args:
            data (Dict[str, str]): Claims to encode (typically {"sub": username}).

        Returns:
            str: The encoded JWT string.
        """
        to_encode = data.copy()
        expire = datetime.now(timezone.utc) + timedelta(
            days=self._settings.refresh_token_expire_days
        )
        to_encode[JWT_EXP_CLAIM] = expire
        to_encode[JWT_TYPE_CLAIM] = REFRESH_TOKEN_TYPE
        logger.debug(f"Creating refresh token for {data.get(JWT_SUB_CLAIM)}")
        return jwt.encode(
            to_encode,
            self._settings.jwt_secret,
            algorithm=self._settings.jwt_algorithm,
        )

    def decode_token(
        self, token: str, expected_type: str = ACCESS_TOKEN_TYPE
    ) -> Dict:
        """Decode and validate a JWT token.

        Args:
            token (str): The JWT string to decode.
            expected_type (str): Expected token type ("access" or "refresh").

        Returns:
            Dict: The decoded token payload.

        Raises:
            TokenExpiredError: If the token has expired.
            AuthenticationError: If the token is invalid or wrong type.
        """
        try:
            payload = jwt.decode(
                token,
                self._settings.jwt_secret,
                algorithms=[self._settings.jwt_algorithm],
            )
        except JWTError as err:
            logger.warning(f"JWT decode failed: {err}")
            raise AuthenticationError("Invalid token") from err
        if payload.get(JWT_TYPE_CLAIM) != expected_type:
            raise AuthenticationError(
                f"Expected {expected_type} token, got {payload.get('type')}"
            )
        return payload
