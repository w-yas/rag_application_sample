import json
import os
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.routing import APIRoute
from starlette.exceptions import HTTPException
from starlette.middleware.cors import CORSMiddleware

from back.api.middlewares.request_id_middleware import RequestIDMiddleware
from back.api.routes.route import router
from back.api.utils.exception_handler import (
    generic_exception_handler,
    http_exception_handler,
    validation_exception_handler,
)
from back.api.utils.logging import logger


@asynccontextmanager
async def lifespan(app: FastAPI):
    if os.getenv("ENV") == "development":
        try:
            out_path = Path(__file__).parent.parent.parent / "openapi.json"
            out_path.parent.mkdir(parents=True, exist_ok=True)
            with out_path.open("w") as f:
                json.dump(app.openapi(), f, indent=2)
                logger.info(
                    "OpenAPI スキーマの書き込みに成功しました %s",
                    out_path,
                    extra={"request_id": ""},
                )
        except Exception as e:
            logger.error(
                "OpenAPI スキーマの書き込み中にエラーが発生しました %s",
                e,
                extra={"request_id": ""},
            )
        yield


def create_app() -> FastAPI:
    application = FastAPI(
        lifespan=lifespan,
    )

    application.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["POST", "GET"],
        allow_headers=["*"],
        expose_headers=["x-request-id"],
    )

    # ミドルウェアの追加
    application.add_middleware(RequestIDMiddleware)
    application.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=os.getenv("TRUSTED_HOSTS", "*").split(","),
    )

    application.include_router(router)
    return application


# API ドキュメントで route 名を operationId とする
def use_route_names_as_operation_ids(app: FastAPI) -> None:
    for route in app.routes:
        if isinstance(route, APIRoute):
            route.operation_id = route.name


app = create_app()

# 既定の HTTPException 処理のオーバーライド
app.add_exception_handler(HTTPException, http_exception_handler)
# リクエストバリデーションエラー(422) のハンドラ
app.add_exception_handler(RequestValidationError, validation_exception_handler)
# 未処理例外のハンドラ（Exception を捕ることで 500 を一元化）
app.add_exception_handler(Exception, generic_exception_handler)


use_route_names_as_operation_ids(app)
