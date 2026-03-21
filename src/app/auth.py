"""API key authentication dependency."""

import hmac

from fastapi import Depends, HTTPException, Query, Request, status
from fastapi.security import APIKeyHeader

from app.config import settings

_api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


async def require_api_key(
    request: Request,
    header_key: str | None = Depends(_api_key_header),
    query_key: str | None = Query(default=None, alias="api_key", include_in_schema=False),
) -> None:
    """Validate API key from header or query parameter. No-op if auth is disabled."""
    if not settings.auth_enabled:
        return

    provided_key = header_key or query_key
    if not provided_key or not hmac.compare_digest(provided_key, settings.api_key):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API key",
        )
