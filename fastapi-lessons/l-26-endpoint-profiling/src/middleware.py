from fastapi import Request
from fastapi.responses import HTMLResponse
from starlette.middleware.base import BaseHTTPMiddleware
from pyinstrument import Profiler

from src.config import settings


class ProfilingMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, profile_initiating_query_param: str = 'profile'):
        super().__init__(app)
        self.profile_initiating_query_param = profile_initiating_query_param

    async def dispatch(self, request: Request, call_next):
        profiling = request.query_params.get(self.profile_initiating_query_param, False)
        if profiling and settings.ENABLE_ENDPOINT_PROFILING:
            profiler = Profiler()
            profiler.start()
            await call_next(request)
            profiler.stop()
            return HTMLResponse(profiler.output_html())
        else:
            return await call_next(request)
