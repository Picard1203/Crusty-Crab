"""Schemas package."""

from src.schemas.auth import (
    TokenRefreshRequest,
    TokenResponse,
    UserCreate,
    UserResponse,
    UserUpdate,
)
from src.schemas.base_request import BaseRequest
from src.schemas.base_response import BaseResponse
from src.schemas.menu_item import (
    MenuItemCreate,
    MenuItemResponse,
    MenuItemUpdate,
)
from src.schemas.order import (
    OrderCreate,
    OrderCreateResponse,
    OrderFilter,
    OrderListResponse,
    OrderResponse,
    OrderStatusUpdate,
    OrderUpdate,
    OrderUpdateResponse,
)
from src.schemas.paginated_response import PaginatedResponse
from src.schemas.statistics import (
    BusiestHourResponse,
    DailyProfitsResponse,
    OrderStatusBreakdownResponse,
    StatisticsResponse,
    TopCustomerResponse,
)

