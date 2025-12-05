import time
import uuid
from typing import Any

from litestar import Request, Response
from litestar.middleware import DefineMiddleware
from litestar.types import ASGIApp, Receive, Scope, Send

from app.infrastructure.logging import bind_trace_id, get_logger

logger = get_logger(__name__)


class TraceIDMiddleware:
    def __init__(self, app: ASGIApp):
        self.app = app
    
    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        
        request = Request(scope)
        trace_id = request.headers.get("X-Request-Id", str(uuid.uuid4()))
        bind_trace_id(trace_id)
        
        start_time = time.time()
        
        logger.info(
            "Request started",
            method=request.method,
            path=request.url.path,
            trace_id=trace_id
        )
        
        async def send_wrapper(message: dict[str, Any]) -> None:
            if message["type"] == "http.response.start":
                headers = list(message.get("headers", []))
                headers.append((b"x-trace-id", trace_id.encode()))
                message["headers"] = headers
                
                duration = time.time() - start_time
                status_code = message.get("status", 200)
                
                logger.info(
                    "Request completed",
                    method=request.method,
                    path=request.url.path,
                    status_code=status_code,
                    duration=f"{duration:.3f}s",
                    trace_id=trace_id
                )
            
            await send(message)
        
        try:
            await self.app(scope, receive, send_wrapper)
        except Exception as e:
            logger.error(
                "Request failed",
                method=request.method,
                path=request.url.path,
                error=str(e),
                trace_id=trace_id
            )
            raise


trace_id_middleware = DefineMiddleware(TraceIDMiddleware)
