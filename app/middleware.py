import logging
import time
from uuid import uuid4

from prometheus_client import Counter, Histogram
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

logger = logging.getLogger("ferreteria.http")

REQUESTS = Counter(
    "ferreteria_http_requests_total",
    "Total HTTP requests",
    ["method", "status"],
)
LATENCY = Histogram(
    "ferreteria_http_request_duration_seconds",
    "HTTP request duration in seconds",
    ["method"],
)


class RequestContextMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        request_id = request.headers.get("X-Request-ID") or f"req_{uuid4().hex}"
        request.state.request_id = request_id
        started = time.perf_counter()

        response = await call_next(request)
        elapsed = time.perf_counter() - started
        response.headers["X-Request-ID"] = request_id

        REQUESTS.labels(request.method, str(response.status_code)).inc()
        LATENCY.labels(request.method).observe(elapsed)
        logger.info(
            "http_request_completed",
            extra={
                "request_id": request_id,
                "method": request.method,
                "path": request.url.path,
                "status_code": response.status_code,
                "duration_ms": round(elapsed * 1_000, 2),
            },
        )
        return response
