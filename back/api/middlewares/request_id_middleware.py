import time
import uuid
from starlette.types import ASGIApp, Scope, Receive, Send, Message
from back.api.utils.logging import logger
from back.api.utils.add_request_id import set_request_id
from fastapi.responses import JSONResponse
from fastapi import status


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
