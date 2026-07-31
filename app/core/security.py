import secrets

from fastapi import Header, HTTPException, status

from app.core.config import settings


def require_admin_key(
    x_admin_key: str | None = Header(default=None),
) -> None:
    expected = settings.admin_api_key.get_secret_value()
    if x_admin_key is None or not secrets.compare_digest(x_admin_key, expected):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid or missing administrator credential",
        )
