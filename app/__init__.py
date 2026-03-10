"""
TicketIA API - Quart application factory.
"""
import logging
import logging.config
from quart import Quart
from quart_cors import cors

from app.config import get_settings
from app.utils.exceptions import TicketIABaseError
from app.utils.response import error_response


def create_app() -> Quart:
    """Create and configure the Quart application."""
    settings = get_settings()

    # Configure structured logging
    logging.basicConfig(
        level=getattr(logging, settings.log_level.upper(), logging.INFO),
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )

    app = Quart(__name__)
    app.secret_key = settings.app_secret_key

    # CORS
    app = cors(
        app,
        allow_origin=settings.cors_origins_list,
        allow_headers=["Content-Type", "Authorization"],
        allow_methods=["GET", "POST", "PATCH", "DELETE", "OPTIONS"],
    )

    # Register blueprints under /api prefix
    from app.routes.health import health_bp
    from app.routes.tickets import tickets_bp
    from app.routes.categories import categories_bp
    from app.routes.providers import providers_bp

    app.register_blueprint(health_bp, url_prefix="/api")
    app.register_blueprint(tickets_bp, url_prefix="/api")
    app.register_blueprint(categories_bp, url_prefix="/api")
    app.register_blueprint(providers_bp, url_prefix="/api")

    # Global error handlers
    @app.errorhandler(TicketIABaseError)
    async def handle_ticketia_error(exc: TicketIABaseError):
        return error_response(exc.message, errors=exc.details, status_code=exc.status_code)

    @app.errorhandler(404)
    async def handle_not_found(exc):
        return error_response("Endpoint not found", status_code=404)

    @app.errorhandler(405)
    async def handle_method_not_allowed(exc):
        return error_response("Method not allowed", status_code=405)

    @app.errorhandler(500)
    async def handle_internal_error(exc):
        logging.getLogger(__name__).exception("Unhandled internal error")
        return error_response("Internal server error", status_code=500)

    return app
