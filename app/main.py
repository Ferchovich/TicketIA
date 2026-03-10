"""
Entry point for TicketIA API.
Run with: python -m app.main
or: hypercorn app.main:app
"""
import asyncio
import logging

from app import create_app
from app.config import get_settings

logger = logging.getLogger(__name__)

app = create_app()


if __name__ == "__main__":
    settings = get_settings()
    import hypercorn.asyncio
    from hypercorn.config import Config

    config = Config()
    config.bind = [f"{settings.app_host}:{settings.app_port}"]
    config.loglevel = settings.log_level.lower()

    logger.info("Starting TicketIA API on %s:%s", settings.app_host, settings.app_port)
    asyncio.run(hypercorn.asyncio.serve(app, config))
