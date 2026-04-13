from __future__ import annotations

import secrets
from typing import Any

from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.responses import Response


class ApiKeyMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: Any, api_keys: list[str]):
        super().__init__(app)
        self.api_keys = api_keys
        self.public_paths = [
            "/",
            "/livez",
            "/readyz",
            "/docs",
            "/openapi.json",
            "/redoc",
        ]

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        if request.method == "OPTIONS":
            return await call_next(request)

        if request.url.path not in self.public_paths:
            api_key = request.headers.get("X-API-KEY")
            if api_key is not None:
                api_key = api_key.strip()
            is_valid = any(secrets.compare_digest(api_key, valid_key) for valid_key in self.api_keys)
            if not is_valid:
                return JSONResponse(status_code=401, content={"detail": "Unauthorized"})
        response = await call_next(request)
        return response
