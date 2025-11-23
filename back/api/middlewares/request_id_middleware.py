import time
import uuid

from fastapi import status
from fastapi.responses import JSONResponse
from starlette.types import ASGIApp, Message, Receive, Scope, Send

from back.api.utils.add_request_id import set_request_id
from back.api.utils.logging import logger


# NOTE: contextvarが正しく機能するためにBaseHTTPMiddlewareではなくASGIミドルウェアを使用
class RequestIDMiddleware:
    def __init__(self, app: ASGIApp):
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            try:
                await self.app(scope, receive, send)
            except Exception as e:
                return JSONResponse(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    content={"error": "Internal Server Error", "detail": str(e)},
                )
            return

        # 受信ヘッダに x-request-id があれば使い、なければ新規生成
        request_id = None
        headers = scope.get("headers", [])
        for name, value in headers:
            if name.decode("latin1").lower() == "x-request-id":
                try:
                    request_id = value.decode("utf-8")
                except Exception:
                    request_id = value.decode("latin1")
                break

        if not request_id:
            request_id = str(uuid.uuid4())

        set_request_id(request_id)
        start = time.time()

        # send をラップしてレスポンスヘッダに X-Request-ID を追加できるようにする
        async def send_wrapper(message: Message) -> None:
            # 200系ステータスなどの start_event にヘッダを付与
            if message["type"] == "http.response.start":
                headers = list(message.get("headers", []))
                headers.append((b"x-request-id", request_id.encode()))
                message["headers"] = headers
            await send(message)

        try:
            await self.app(scope, receive, send_wrapper)
        except Exception as e:
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={"error": "Internal Server Error", "detail": str(e)},
            )

        finally:
            duration_ms = (time.time() - start) * 1000
            logger.info(
                "request completed",
                extra={
                    "request_id": request_id,
                    "path": scope.get("path"),
                    "method": scope.get("method"),
                    "duration_ms": round(duration_ms, 2),
                },
            )
