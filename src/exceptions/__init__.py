"""Exceptions package."""

from src.exceptions.app_exception import AppException
from src.exceptions.authentication_error import AuthenticationError
from src.exceptions.authorization_error import AuthorizationError
from src.exceptions.duplicate_error import DuplicateError
from src.exceptions.invalid_operation_error import InvalidOperationError
from src.exceptions.invalid_status_transition_error import (
    InvalidStatusTransitionError,
)
from src.exceptions.menu_item_unavailable_error import (
    MenuItemUnavailableError,
)
from src.exceptions.not_found_error import NotFoundError
from src.exceptions.order_not_modifiable_error import OrderNotModifiableError
from src.exceptions.token_expired_error import TokenExpiredError
from src.exceptions.validation_error import ValidationError
