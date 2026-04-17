"""Unit tests for AuthService."""

from datetime import datetime, timezone
from unittest.mock import AsyncMock

import pytest
from bson import ObjectId

from src.auth.password_handler import PasswordHandler
from src.auth.token_handler import TokenHandler
from src.enums import UserRole
from src.exceptions import AuthenticationError, DuplicateError
from src.models.user_document import UserDocument
from src.schemas.auth.user_create import UserCreate
from src.services.auth_service import AuthService


def _make_user(
    username: str = "testuser",
    email: str = "test@example.com",
    is_active: bool = True,
) -> UserDocument:
    """Build a UserDocument for testing.

    Args:
        username (str): The username.
        email (str): The email address.
        is_active (bool): Whether the account is active.

    Returns:
        UserDocument: A test user document.
    """
    ph = PasswordHandler()
    return UserDocument.model_construct(
        id=ObjectId(),
        username=username,
        email=email,
        hashed_password=ph.hash_password("correct-password"),
        role=UserRole.GUEST,
        is_active=is_active,
        created_at=datetime.now(timezone.utc),
    )


@pytest.mark.asyncio
class TestRegister:
    """Tests for AuthService.register."""

    async def test_registers_successfully(
        self,
        mock_user_repo: AsyncMock,
        password_handler: PasswordHandler,
        token_handler: TokenHandler,
    ) -> None:
        """Valid registration creates a user with hashed password.

        Args:
            mock_user_repo (AsyncMock): Mocked user repository.
            password_handler (PasswordHandler): Real password handler.
            token_handler (TokenHandler): Real token handler.
        """
        user = _make_user()
        mock_user_repo.get_by_username.return_value = None
        mock_user_repo.get_by_email.return_value = None
        mock_user_repo.create.return_value = user
        service = AuthService(mock_user_repo, password_handler, token_handler)
        data = UserCreate(
            username="testuser",
            email="test@example.com",
            password="securepassword",
        )
        result = await service.register(data)
        assert result.username == "testuser"

    async def test_raises_duplicate_on_existing_username(
        self,
        mock_user_repo: AsyncMock,
        password_handler: PasswordHandler,
        token_handler: TokenHandler,
    ) -> None:
        """Existing username raises DuplicateError.

        Args:
            mock_user_repo (AsyncMock): Mocked user repository.
            password_handler (PasswordHandler): Real password handler.
            token_handler (TokenHandler): Real token handler.
        """
        mock_user_repo.get_by_username.return_value = _make_user()
        service = AuthService(mock_user_repo, password_handler, token_handler)
        data = UserCreate(
            username="testuser",
            email="new@example.com",
            password="securepassword",
        )
        with pytest.raises(DuplicateError):
            await service.register(data)

    async def test_raises_duplicate_on_existing_email(
        self,
        mock_user_repo: AsyncMock,
        password_handler: PasswordHandler,
        token_handler: TokenHandler,
    ) -> None:
        """Existing email raises DuplicateError.

        Args:
            mock_user_repo (AsyncMock): Mocked user repository.
            password_handler (PasswordHandler): Real password handler.
            token_handler (TokenHandler): Real token handler.
        """
        mock_user_repo.get_by_username.return_value = None
        mock_user_repo.get_by_email.return_value = _make_user()
        service = AuthService(mock_user_repo, password_handler, token_handler)
        data = UserCreate(
            username="newuser",
            email="test@example.com",
            password="securepassword",
        )
        with pytest.raises(DuplicateError):
            await service.register(data)


@pytest.mark.asyncio
class TestAuthenticate:
    """Tests for AuthService.authenticate."""

    async def test_returns_tokens_on_valid_credentials(
        self,
        mock_user_repo: AsyncMock,
        password_handler: PasswordHandler,
        token_handler: TokenHandler,
    ) -> None:
        """Valid credentials return access and refresh tokens.

        Args:
            mock_user_repo (AsyncMock): Mocked user repository.
            password_handler (PasswordHandler): Real password handler.
            token_handler (TokenHandler): Real token handler.
        """
        user = _make_user()
        mock_user_repo.get_by_username.return_value = user
        service = AuthService(mock_user_repo, password_handler, token_handler)
        result = await service.authenticate("testuser", "correct-password")
        assert result.access_token
        assert result.refresh_token

    async def test_raises_on_wrong_password(
        self,
        mock_user_repo: AsyncMock,
        password_handler: PasswordHandler,
        token_handler: TokenHandler,
    ) -> None:
        """Wrong password raises AuthenticationError.

        Args:
            mock_user_repo (AsyncMock): Mocked user repository.
            password_handler (PasswordHandler): Real password handler.
            token_handler (TokenHandler): Real token handler.
        """
        user = _make_user()
        mock_user_repo.get_by_username.return_value = user
        service = AuthService(mock_user_repo, password_handler, token_handler)
        with pytest.raises(AuthenticationError):
            await service.authenticate("testuser", "wrong-password")

    async def test_raises_on_inactive_user(
        self,
        mock_user_repo: AsyncMock,
        password_handler: PasswordHandler,
        token_handler: TokenHandler,
    ) -> None:
        """Inactive user raises AuthenticationError.

        Args:
            mock_user_repo (AsyncMock): Mocked user repository.
            password_handler (PasswordHandler): Real password handler.
            token_handler (TokenHandler): Real token handler.
        """
        user = _make_user(is_active=False)
        mock_user_repo.get_by_username.return_value = user
        service = AuthService(mock_user_repo, password_handler, token_handler)
        with pytest.raises(AuthenticationError):
            await service.authenticate("testuser", "correct-password")
