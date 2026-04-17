"""Schemas package."""

from src.schemas.auth_models import (
    TokenRefreshRequest,
    TokenResponse,
    UserCreate,
    UserResponse,
    UserUpdate,
)
from src.schemas.base_request import BaseRequest
from src.schemas.base_response import BaseResponse
from src.schemas.menu_item_models import (
    MenuItemCreate,
    MenuItemResponse,
    MenuItemUpdate,
)
from src.schemas.order_models import (
    OrderBase,
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
from src.schemas.statistics_models import (
    BusiestHourResponse,
    DailyProfitsResponse,
    OrderStatusBreakdownResponse,
    StatisticsResponse,
    TopCustomerResponse,
)
