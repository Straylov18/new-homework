import time
from typing import Awaitable, Callable

from fastapi import FastAPI, Request, Response, status
from starlette.middleware.base import BaseHTTPMiddleware

from src.metrics.http_requests import (api_calls_total, http_errors_4xx_total,
                                       http_errors_5xx_total,
                                       http_request_duration_seconds,
                                       http_requests_total)


class MetricsMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: FastAPI) -> None:
        super().__init__(app)

    async def dispatch(self, request: Request, call_next: Callable[[Request], Awaitable[Response]]) -> Response:
        # executing request
        start_time = time.time()
        try:
            response = await call_next(request)
        except Exception as e:
            response = Response(
                content=str(e),
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                media_type="text/plain"
            )
        duration = time.time() - start_time

        path = request.url.path
        # normalize paths: /api/v1/activities/12345 -> /api/v1/activities/{uid}
        if path.startswith('/api/v1/'):
            parts = path.split('/')
            if len(parts) >= 4 and parts[4].isdigit():
                parts[4] = '{uid}'
                path = '/'.join(parts)

        # collecting metrics
        http_requests_total.labels(
            method=request.method,
            endpoint=path,
            status_code=str(response.status_code)
        ).inc()

        http_request_duration_seconds.labels(
            method=request.method,
            endpoint=path
        ).observe(duration)

        # tracking API calls
        if path.startswith('/api/v1/'):
            if len(path.split('/')) >= 3:
                api_type = path.split('/')[3]
            else:
                api_type = 'unknown'
            api_calls_total.labels(api_type=api_type).inc()

        # separate errors counting
        status_code = response.status_code
        if 400 <= status_code <= 500:
            http_errors_4xx_total.labels(endpoint=path, status_code=str(status_code)).inc()
        elif status_code >= 500:
            http_errors_5xx_total.labels(endpoint=path, status_code=str(status_code)).inc()

        return response
