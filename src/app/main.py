"""FastAPI application factory and entrypoint."""

import logging
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from app import __version__
from app.config import settings
from app.routes import admin, forecast, health
from app.services.cache import cache
from app.services.fetcher import close_client

logging.basicConfig(
    level=getattr(logging, settings.log_level.upper(), logging.INFO),
    format="%(asctime)s %(levelname)s %(name)s — %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

FRONTEND_DIR = Path(__file__).resolve().parent.parent.parent / "frontend" / "dist"


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup/shutdown lifecycle manager."""
    logger.info("Starting Puget Sound Marine Forecast API v%s", __version__)
    await cache.start_background_refresh()

    try:
        if settings.mcp_enabled:
            from app.mcp.server import mcp_server

            async with mcp_server.session_manager.run():
                yield
        else:
            yield
    finally:
        logger.info("Shutting down...")
        await cache.stop_background_refresh()
        await close_client()


def create_app() -> FastAPI:
    app = FastAPI(
        title="Puget Sound Marine Forecast API",
        description="Marine forecast service for Puget Sound — REST API, MCP server, and web UI",
        version=__version__,
        lifespan=lifespan,
    )

    # CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "OPTIONS"],
        allow_headers=["*"],
    )

    # Global error handler
    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        logger.error("Unhandled exception: %s", exc, exc_info=True)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": "Internal server error"},
        )

    # Register routers
    app.include_router(health.router)
    app.include_router(forecast.router)
    app.include_router(admin.router)

    # Mount MCP server if enabled
    if settings.mcp_enabled:
        # Mount the raw Starlette app without its own lifespan — we manage
        # the session_manager in our own lifespan above.

        from app.mcp.server import mcp_server

        mcp_app = mcp_server.streamable_http_app()
        # Replace lifespan to avoid double-init of session manager
        mcp_app.router.lifespan_context = None
        app.mount("/mcp", mcp_app)
        logger.info("MCP server mounted at /mcp")

    # Serve React frontend (if built)
    if FRONTEND_DIR.is_dir():
        app.mount("/assets", StaticFiles(directory=FRONTEND_DIR / "assets"), name="static")

        @app.get("/{path:path}")
        async def serve_spa(path: str):
            """Serve the React SPA — fallback to index.html for client-side routing."""
            file = FRONTEND_DIR / path
            if file.is_file():
                return FileResponse(file)
            return FileResponse(FRONTEND_DIR / "index.html")

        logger.info("Frontend served from %s", FRONTEND_DIR)

    return app


app = create_app()

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=False,
    )
