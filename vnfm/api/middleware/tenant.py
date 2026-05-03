from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware


class TenantMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        tenant_id = request.headers.get("X-Tenant-Id")
        request.state.tenant_id = tenant_id
        response = await call_next(request)
        return response
