"""FastAPI application factory and configuration."""

import logging
from contextlib import asynccontextmanager
from datetime import datetime, timezone

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

from src.constants.menu_constants import DEFAULT_MENU_ITEMS
from src.constants.sequence_constants import MENU_ITEM_NUMBER_SEQUENCE
from src.database.mongodb import MongoDatabase
from src.exceptions import AppException
from src.logging import setup_logging
from src.middleware import RequestLoggingMiddleware
from src.models import MenuItemDocument
from src.repositories.mongodb import (
    MongoCounterRepository,
    MongoMenuItemRepository,
)
from src.routes import (
    auth_router,
    menu_router,
    order_router,
    profits_router,
    statistics_router,
    user_router,
)
from src.settings import get_settings

logger = logging.getLogger(__name__)
limiter = Limiter(key_func=get_remote_address)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application startup and shutdown lifecycle.

    Args:
        app (FastAPI): The FastAPI application instance.

    Yields:
        None: Control is yielded to the running application between startup
            and shutdown.
    """
    settings = get_settings()
    setup_logging(settings.log_level)
    database = MongoDatabase()
    app.state.database = database
    await database.connect()
    await database.init_models()
    await _seed_menu_if_empty()
    logger.info("Application startup complete")
    yield
    await database.disconnect()
    logger.info("Application shutdown complete")


async def _seed_menu_if_empty() -> None:
    """Seed default menu items if the menu_items collection is empty.

    Uses the counter repository to assign auto-increment item numbers
    and inserts the DEFAULT_MENU_ITEMS seed data on first startup.
    """
    menu_repo = MongoMenuItemRepository()
    existing_count = await menu_repo.count({})
    if existing_count > 0:
        logger.info(
            f"Menu collection already has {existing_count} items, "
            "skipping seed"
        )
        return
    logger.info("Seeding default menu items")
    counter_repo = MongoCounterRepository()
    now = datetime.now(timezone.utc)
    for item_data in DEFAULT_MENU_ITEMS:
        item_number = await counter_repo.get_next_sequence(
            MENU_ITEM_NUMBER_SEQUENCE
        )
        item = MenuItemDocument(
            item_number=item_number,
            name=item_data["name"],
            price=item_data["price"],
            is_active=True,
            created_at=now,
            updated_at=now,
        )
        await menu_repo.create(item)
        logger.info(
            f"Seeded menu item #{item_number}: {item_data['name']}"
        )


def create_app() -> FastAPI:
    """Create and configure the FastAPI application instance.

    Returns:
        FastAPI: The configured application with exception handlers registered.
    """
    settings = get_settings()
    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        lifespan=lifespan,
    )
    app.state.limiter = limiter
    register_exception_handlers(app)
    register_middleware(app, settings)
    register_routers(app)
    return app


def register_exception_handlers(app: FastAPI) -> None:
    """Register global exception handlers on the application.

    Args:
        app (FastAPI): The FastAPI application instance to register handlers on.
    """

    @app.exception_handler(AppException)
    async def _app_exception_handler(
        _request: Request, exc: AppException
    ) -> JSONResponse:
        logger.warning(
            f"Domain exception: {exc.__class__.__name__} - {exc.message}"
        )
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.message},
        )

    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


def register_middleware(app: FastAPI, settings) -> None:
    """Register all middleware on the application.

    Args:
        app (FastAPI): The FastAPI application instance.
        settings: Application settings for CORS and rate limit config.
    """
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.add_middleware(RequestLoggingMiddleware)


def register_routers(app: FastAPI) -> None:
    """Register all API routers on the application.

    Args:
        app (FastAPI): The FastAPI application instance.
    """
    app.include_router(auth_router)
    app.include_router(order_router)
    app.include_router(menu_router)
    app.include_router(profits_router)
    app.include_router(statistics_router)
    app.include_router(user_router)


app = create_app()
