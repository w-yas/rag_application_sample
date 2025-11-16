from fastapi import Request
import os
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.status import HTTP_500_INTERNAL_SERVER_ERROR
from typing import Any
from back.api.utils.add_request_id import get_request_id
from fastapi.responses import JSONResponse
import traceback


# Starletteの内部コードやStarletteの拡張機能やプラグインの一部がHTTPExceptionを発生させた場合、ハンドラがそれをキャッチして処理する
async def http_exception_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
    headers = getattr(
        exc, "headers", None
    )  # Fast APIのHTTPExceptionの場合はレスポンスに含まれるヘッダを追加できる
    payload: dict[str, Any] = {
        "message": "HTTP Exception",
        "detail": exc.detail,
        "request_id": get_request_id(),
        "path": str(request.url.path),
    }
    return JSONResponse(content=payload, status_code=exc.status_code, headers=headers)


async def validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    detail = exc.errors()
    payload: dict[str, Any] = {
        "message": "Validation Error",
        "detail": detail,
        "request_id": get_request_id() or None,
        "path": str(request.url.path),
    }
    return JSONResponse(content=payload, status_code=422)


async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    payload: dict[str, Any] = {
        "message": "Internal Server Error",
        "detail": "An unexpected error occured",
        "request_id": get_request_id(),
        "path": str(request.url.path),
    }
    if os.getenv("ENV") == "develop":
        tb = "".join(traceback.format_exception(type(exc), exc, exc.__traceback__))
        payload["debug"] = tb
    return JSONResponse(content=payload, status_code=HTTP_500_INTERNAL_SERVER_ERROR)
