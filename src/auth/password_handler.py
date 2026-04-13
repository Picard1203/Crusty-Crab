"""Password hashing and verification using bcrypt."""

import logging

import bcrypt

logger = logging.getLogger(__name__)


class PasswordHandler:
    """Handles password hashing and verification."""

    def hash_password(self, password: str) -> str:
        """Hash a plaintext password.

        Args:
            password (str): The plaintext password to hash.

        Returns:
            str: The bcrypt hash string.
        """
        logger.debug("Hashing password")
        return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

    def verify_password(self, plain: str, hashed: str) -> bool:
        """Verify a plaintext password against a stored hash.

        Args:
            plain (str): The plaintext password to check.
            hashed (str): The stored bcrypt hash.

        Returns:
            bool: True if the password matches, False otherwise.
        """
        return bcrypt.checkpw(plain.encode(), hashed.encode())
