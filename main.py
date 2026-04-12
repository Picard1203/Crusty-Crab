"""Application entry point."""

from src.app import app
from src.settings import get_settings

if __name__ == "__main__":
    import uvicorn

    _settings = get_settings()
    uvicorn.run(app, host=_settings.host, port=_settings.port)
