"""Application settings loaded from environment variables."""

from functools import lru_cache
from typing import List

from pydantic import computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Settings class for the Krusty Crab API configuration.

    Attributes:
        host (str): The host address the server binds to. Defaults to "0.0.0.0".
        port (int): The port the server listens on. Defaults to 8000.
        app_name (str): The name of the application.
            Defaults to "The Krusty Crab".
        app_version (str): The semantic version of the application.
            Defaults to "1.0.0".
        debug (bool): Flag to enable/disable debug mode. Defaults to False.
        log_level (str): The logging level for the application.
            Defaults to "INFO".
        mongodb_host (str): MongoDB server hostname. Defaults to "127.0.0.1".
        mongodb_port (int): MongoDB server port. Defaults to 27017.
        mongodb_url (str): Computed MongoDB connection string built from
            host and port.
        database_name (str): The name of the MongoDB database.
            Defaults to "krusty_crab_api".
        jwt_secret (str): Secret key used for JWT token signing.
            Required — no default.
        jwt_algorithm (str): Algorithm used for JWT token encoding.
            Defaults to "HS256".
        access_token_expire_minutes (int): Token expiration time in minutes.
            Defaults to 30.
        refresh_token_expire_days (int): Refresh token expiration time in days.
            Defaults to 7.
        allowed_origins (List[str]): List of allowed CORS origins.
            Defaults to ["http://localhost:3000"].
        rate_limit_per_minute (int): Maximum API requests allowed per minute.
            Defaults to 60.
        pagination_default_limit (int): Default number of items per page.
            Defaults to 10.
        pagination_max_limit (int): Maximum allowed items per page.
            Defaults to 100.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
    )

    # Server
    host: str = "0.0.0.0"
    port: int = 8000

    # Application
    app_name: str = "The Krusty Crab"
    app_version: str = "1.0.0"
    debug: bool = False
    log_level: str = "INFO"

    # MongoDB
    mongodb_host: str = "127.0.0.1"
    mongodb_port: int = 27017
    database_name: str = "krusty_crab_api"

    @computed_field
    @property
    def mongodb_url(self) -> str:
        """Build MongoDB connection URL from host and port."""
        return (
            f"mongodb://{self.mongodb_host}:{self.mongodb_port}/?replicaSet=rs0"
        )

    # JWT
    jwt_secret: str
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7

    # CORS
    allowed_origins: List[str] = ["http://localhost:3000"]

    # Rate Limiting
    rate_limit_per_minute: int = 60

    # Pagination
    pagination_default_limit: int = 10
    pagination_max_limit: int = 100


@lru_cache()
def get_settings() -> Settings:
    """Return cached Settings instance (singleton pattern).

    Returns:
        Settings: The application settings singleton.
    """
    return Settings()
