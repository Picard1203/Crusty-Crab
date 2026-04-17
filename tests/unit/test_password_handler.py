"""Unit tests for PasswordHandler."""

from src.auth.password_handler import PasswordHandler


class TestPasswordHandler:
    """Tests for password hashing and verification."""

    def test_hash_returns_bcrypt_string(
        self, password_handler: PasswordHandler
    ) -> None:
        """Verify that hash_password generates a valid bcrypt string.

        Args:
            password_handler (PasswordHandler): The initialized PasswordHandler.
        """
        hashed: str = password_handler.hash_password("mysecret")
        assert hashed.startswith("$2b$")
        assert hashed != "mysecret"

    def test_verify_correct_password(
        self, password_handler: PasswordHandler
    ) -> None:
        """Correct password returns True.

        Args:
            password_handler (PasswordHandler): The initialized PasswordHandler.
        """
        hashed: str = password_handler.hash_password("mysecret")
        assert password_handler.verify_password("mysecret", hashed) is True

    def test_verify_wrong_password(
        self, password_handler: PasswordHandler
    ) -> None:
        """Wrong password returns False.

        Args:
            password_handler (PasswordHandler): The initialized PasswordHandler.
        """
        hashed: str = password_handler.hash_password("mysecret")
        assert password_handler.verify_password("wrongpass", hashed) is False

    def test_same_password_different_hashes(
        self, password_handler: PasswordHandler
    ) -> None:
        """Same plaintext produces different hashes (salt uniqueness).

        Args:
            password_handler (PasswordHandler): The initialized PasswordHandler.
        """
        hash1: str = password_handler.hash_password("mysecret")
        hash2: str = password_handler.hash_password("mysecret")
        assert hash1 != hash2
