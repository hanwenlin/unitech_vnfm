from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

from vnfm.api.auth.security import decode_token


class TenantMiddleware(BaseHTTPMiddleware):
    """Populate ``request.state.tenant_id`` and ``request.state.user`` from a verified JWT.

    Tenant identity is derived solely from the signed token; the legacy
    ``X-Tenant-Id`` header is intentionally ignored to prevent client-side spoofing.
    Routes should still depend on ``get_current_user`` for full validation; this
    middleware exists as a fallback for code paths that read ``request.state``.
    """

    async def dispatch(self, request: Request, call_next):
        request.state.tenant_id = None
        request.state.user = None

        auth_header = request.headers.get("Authorization", "")
        if auth_header.startswith("Bearer "):
            token = auth_header[len("Bearer "):]
            payload = decode_token(token)
            if payload:
                request.state.tenant_id = payload.get("tenant_id")
                request.state.user = {
                    "username": payload.get("sub"),
                    "role": payload.get("role"),
                    "tenant_id": payload.get("tenant_id"),
                }

        return await call_next(request)
