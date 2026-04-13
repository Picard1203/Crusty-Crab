"""Business logic for authentication operations."""

import logging
from datetime import datetime, timezone

from src.auth.password_handler import PasswordHandler
from src.auth.token_handler import TokenHandler
from src.constants.auth_constants import (
    ACCESS_TOKEN_TYPE,
    JWT_SUB_CLAIM,
    REFRESH_TOKEN_TYPE,
)
from src.exceptions import AuthenticationException, DuplicateException
from src.models import UserDocument
from src.repositories import UserRepository
from src.schemas import TokenResponse, UserCreate

logger = logging.getLogger(__name__)


class AuthService:
    """Orchestrates authentication business logic.

    Attributes:
        _user_repo (UserRepository): User data access.
        _password_handler (PasswordHandler): Password hashing/verification.
        _token_handler (TokenHandler): JWT creation/validation.
    """

    def __init__(
        self,
        user_repo: UserRepository,
        password_handler: PasswordHandler,
        token_handler: TokenHandler,
    ) -> None:
        """Initialize with all dependencies.

        Args:
            user_repo (UserRepository): The user repository interface.
            password_handler (PasswordHandler): Password hashing utility.
            token_handler (TokenHandler): JWT token utility.
        """
        self._user_repo: UserRepository = user_repo
        self._password_handler: PasswordHandler = password_handler
        self._token_handler: TokenHandler = token_handler

    async def register(self, data: UserCreate) -> UserDocument:
        """Register a new API user.

        Args:
            data (UserCreate): The validated registration request.

        Returns:
            UserDocument: The created user document.

        Raises:
            DuplicateException: If username or email already exists.
        """
        logger.info(f"Registering user '{data.username}'")
        await self._check_username(data.username)
        await self._check_email(data.email)
        now = datetime.now(timezone.utc)
        hashed_password = self._password_handler.hash_password(data.password)
        user = UserDocument(
            username=data.username,
            email=data.email,
            hashed_password=hashed_password,
            role=data.role,
            is_active=True,
            created_at=now,
        )
        return await self._user_repo.create(user)

    async def _check_username(self, username: str) -> None:
        """Check if the given username already exists.

        Args:
            username (str): The username to check.

        Raises:
            DuplicateException: If the username already exists.
        """
        existing_user = await self._user_repo.get_by_username(username)
        if existing_user is not None:
            raise DuplicateException(f"Username '{username}' is already taken")

    async def _check_email(self, email: str) -> None:
        """Check if the given email already exists.

        Args:
            email (str): The email to check.

        Raises:
            DuplicateException: If the email already exists.
        """
        existing_user = await self._user_repo.get_by_email(email)
        if existing_user is not None:
            raise DuplicateException(f"Email '{email}' is already registered")

    async def authenticate(
        self, username: str, password: str
    ) -> TokenResponse:
        """Authenticate a user and issue JWT tokens.

        Args:
            username (str): The username to authenticate.
            password (str): The plaintext password to verify.

        Returns:
            TokenResponse: The access and refresh token pair.

        Raises:
            AuthenticationException: If credentials are invalid or user
                is inactive.
        """
        logger.info(f"Authenticating user '{username}'")
        user = await self._user_repo.get_by_username(username)
        if user is None:
            raise AuthenticationException("Invalid username or password")
        if (
            self._password_handler.verify_password(
                password, user.hashed_password
            )
            is False
        ):
            raise AuthenticationException("Invalid username or password")
        if user.is_active is False:
            raise AuthenticationException("User account is deactivated")
        return self._build_token_response(user)

    async def refresh_token(self, refresh_token: str) -> TokenResponse:
        """Issue new tokens using a valid refresh token.

        Args:
            refresh_token (str): The refresh JWT to exchange.

        Returns:
            TokenResponse: A new access and refresh token pair.

        Raises:
            AuthenticationException: If the refresh token is invalid
                or the user no longer exists/is inactive.
        """
        logger.info("Refreshing token")
        username = self._extract_username_from_token(
            refresh_token, REFRESH_TOKEN_TYPE
        )
        user = await self._validate_and_get_active_user(username)
        return self._build_token_response(user)

    async def get_current_user(self, token: str) -> UserDocument:
        """Retrieve the user associated with an access token.

        Args:
            token (str): The access JWT from the Authorization header.

        Returns:
            UserDocument: The authenticated user.

        Raises:
            AuthenticationException: If the token is invalid or user not found.
        """
        username = self._extract_username_from_token(
            token, ACCESS_TOKEN_TYPE
        )
        return await self._validate_and_get_active_user(username)

    async def _validate_and_get_active_user(
        self, username: str
    ) -> UserDocument:
        """Fetch a user by username and verify the account is active.

        Args:
            username (str): The username to look up.

        Returns:
            UserDocument: The validated active user.

        Raises:
            AuthenticationException: If user not found or account is deactivated.
        """
        user = await self._user_repo.get_by_username(username)
        if user is None:
            raise AuthenticationException("User not found")
        if user.is_active is False:
            raise AuthenticationException("User account is deactivated")
        return user

    def _build_token_response(self, user: UserDocument) -> TokenResponse:
        """Build a JWT token pair for the given user.

        Args:
            user (UserDocument): The authenticated user.

        Returns:
            TokenResponse: Access and refresh token pair.
        """
        token_data = {JWT_SUB_CLAIM: user.username}
        return TokenResponse(
            access_token=self._token_handler.create_access_token(token_data),
            refresh_token=self._token_handler.create_refresh_token(
                token_data
            ),
        )

    def _extract_username_from_token(
        self, token: str, expected_type: str
    ) -> str:
        """Decode a token and extract the username claim.

        Args:
            token (str): The JWT to decode.
            expected_type (str): Expected token type.

        Returns:
            str: The extracted username.

        Raises:
            AuthenticationException: If the token payload is invalid.
        """
        payload = self._token_handler.decode_token(
            token, expected_type=expected_type
        )
        username = payload.get(JWT_SUB_CLAIM)
        if username is None:
            raise AuthenticationException("Invalid token payload")
        return username
