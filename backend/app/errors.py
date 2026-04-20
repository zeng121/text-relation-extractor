from collections.abc import Mapping
from typing import Any

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.logging import get_logger

INTERNAL_ERROR_MESSAGE = "An unexpected error occurred."


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(Exception)
    async def handle_unexpected_exception(
        request: Request,  # noqa: ARG001
        exc: Exception,
    ) -> JSONResponse:
        logger = get_logger(__name__)
        logger.exception("Unexpected internal failure during request handling", exc_info=exc)
        payload = _build_internal_error_payload()
        return JSONResponse(status_code=500, content=payload)


def _build_internal_error_payload() -> Mapping[str, Any]:
    return {
        "detail": {
            "code": "internal_error",
            "message": INTERNAL_ERROR_MESSAGE,
        }
    }
