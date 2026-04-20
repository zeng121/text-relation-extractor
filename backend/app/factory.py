from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.logging import configure_logging
from app.routes import extract_router, health_router
from app.settings import Settings


def create_app(settings: Settings | None = None) -> FastAPI:
    configure_logging()
    app = FastAPI(title="Text Graph MVP")
    app.state.settings = settings or Settings()
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.include_router(health_router)
    app.include_router(extract_router)
    return app
