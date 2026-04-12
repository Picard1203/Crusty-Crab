"""JSON structured logging configuration."""

import logging
import os
from logging.handlers import RotatingFileHandler

from pythonjsonlogger import jsonlogger


def configure_json_formatter() -> jsonlogger.JsonFormatter:
    """Configure the JSON formatter for log records.

    Returns:
        jsonlogger.JsonFormatter: The configured JSON formatter.
    """
    return jsonlogger.JsonFormatter(
        fmt="%(asctime)s %(name)s %(levelname)s %(message)s",
        datefmt="%Y-%m-%dT%H:%M:%S",
    )


def setup_stream_handler(
    json_formatter: jsonlogger.JsonFormatter,
) -> logging.StreamHandler:
    """Set up a stream handler for the root logger.

    Args:
        json_formatter (jsonlogger.JsonFormatter): The configured JSON formatter.

    Returns:
        logging.StreamHandler: The configured stream handler.
    """
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(json_formatter)
    return stream_handler


def setup_file_handler(
    log_dir: str, json_formatter: jsonlogger.JsonFormatter
) -> RotatingFileHandler:
    """Set up a file handler for the root logger.

    Args:
        log_dir (str): The directory where log files will be stored.
        json_formatter (jsonlogger.JsonFormatter): The configured JSON formatter.

    Returns:
        RotatingFileHandler: The configured file handler.
    """
    file_handler = RotatingFileHandler(
        filename=os.path.join(log_dir, "app.log"),
        maxBytes=10 * 1024 * 1024,
        backupCount=5,
        encoding="utf-8",
    )
    file_handler.setFormatter(json_formatter)
    return file_handler


def setup_uvicorn_loggers() -> None:
    """Set up the loggers for uvicorn."""
    for uvicorn_logger_name in ["uvicorn", "uvicorn.error", "uvicorn.access"]:
        uvicorn_logger = logging.getLogger(uvicorn_logger_name)
        uvicorn_logger.handlers.clear()
        uvicorn_logger.propagate = True


def setup_logging(log_level: str = "INFO") -> None:
    """Configure application-wide logging.

    Args:
        log_level (str): The root log level (e.g., "INFO", "DEBUG").
    """
    log_dir = "logs"
    os.makedirs(log_dir, exist_ok=True)
    json_formatter = configure_json_formatter()
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    root_logger.handlers.clear()
    stream_handler = setup_stream_handler(json_formatter)
    file_handler = setup_file_handler(log_dir, json_formatter)
    root_logger.addHandler(stream_handler)
    root_logger.addHandler(file_handler)
    setup_uvicorn_loggers()
