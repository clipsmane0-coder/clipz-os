import uuid
import time
import logging
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

logger = logging.getLogger("clipz")


class RequestIDMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
        start_time = time.monotonic()

        request.state.request_id = request_id
        request.state.start_time = start_time

        response: Response = await call_next(request)
        response.headers["X-Request-ID"] = request_id

        duration_ms = int((time.monotonic() - start_time) * 1000)
        extra = {
            "request_id": request_id,
            "duration_ms": duration_ms,
            "method": request.method,
            "path": request.url.path,
        }
        logger.info(f"{request.method} {request.url.path} {response.status_code}", extra=extra)
        return response