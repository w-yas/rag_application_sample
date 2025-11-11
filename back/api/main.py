import json
from contextlib import asynccontextmanager
from pathlib import Path
import os
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from starlette.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from back.api.routes.route import router
from fastapi.routing import APIRoute
from sqlalchemy.orm import exc
from back.api.middlewares.request_id_middleware import RequestIDMiddleware
from back.api.utils.logging import logger


@asynccontextmanager
async def lifespan(app: FastAPI):
    if os.getenv("ENV") == "development":
        try:
            out_path = Path(__file__).parent.parent.parent / "openapi.json"
            out_path.parent.mkdir(parents=True, exist_ok=True)
            with out_path.open("w") as f:
                json.dump(app.openapi(), f, indent=2)
                logger.info(f"OpenAPI スキーマの書き込みに成功しました {out_path}")
        except Exception as e:
            logger.error(f"OpenAPI スキーマの書き込み中にエラーが発生しました: {e}")
        yield


def create_app() -> FastAPI:
    application = FastAPI(
        lifespan=lifespan,
    )

    application.add_middleware(
        CORSMiddleware,
        allow_origins=[
            o.strip() for o in os.getenv("CORS_ALLOW_ORIGINS", "").split(",") if o.strip()
        ],
        allow_credentials=True,
        allow_methods=["POST"],
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
use_route_names_as_operation_ids(app)
