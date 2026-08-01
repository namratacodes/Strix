"""
STRIX backend entrypoint.

Responsibilities kept deliberately minimal here: create the FastAPI app,
wire middleware, and mount routers. All actual logic lives in the
application/domain/infrastructure layers and is reached only through
the api/ routers.
"""

import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1 import health
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

    app.include_router(health.router, prefix=settings.api_v1_prefix)

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
