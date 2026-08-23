"""
STRIX backend entrypoint.
"""

import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware

from app.api.v1 import analyze, auth, health, history
from app.core.config import get_settings
from app.core.logging import configure_logging

settings = get_settings()
configure_logging(debug=settings.debug)
logger = logging.getLogger(__name__)


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.app_name,
        description="Explainable AI Code Intelligence Platform — Every Algorithm Has a Story.",
        version="0.1.0",
        docs_url="/docs",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Signed session cookie -- holds only `user_id` after Google OAuth
    # login (Milestone 10b). Uses the same secret key as everything else
    # session-related, sourced from .env, never hardcoded.
    app.add_middleware(SessionMiddleware, secret_key=settings.session_secret_key)

    app.include_router(health.router, prefix=settings.api_v1_prefix)
    app.include_router(analyze.router, prefix=settings.api_v1_prefix)
    app.include_router(auth.router, prefix=settings.api_v1_prefix)
    app.include_router(history.router, prefix=settings.api_v1_prefix)

    @app.get("/", tags=["root"])
    async def root() -> dict[str, str]:
        return {
            "service": settings.app_name,
            "tagline": "Every Algorithm Has a Story.",
            "docs": "/docs",
        }

    logger.info("STRIX backend initialized (environment=%s)", settings.environment)
    return app


app = create_app()