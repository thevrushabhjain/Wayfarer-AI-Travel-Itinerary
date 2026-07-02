"""Application entry point used by uvicorn (uvicorn server:app)."""

from app.main import app

__all__ = ["app"]
