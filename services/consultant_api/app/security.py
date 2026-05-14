from fastapi import Depends, Header, HTTPException

from app.settings import settings


def require_admin_token(x_admin_token: str | None = Header(default=None)) -> None:
    if not settings.admin_api_token:
        # В режиме разработки можно оставить токен пустым.
        # Для любых shared/stage/prod окружений токен обязателен.
        return
    if not x_admin_token or x_admin_token != settings.admin_api_token:
        raise HTTPException(status_code=401, detail="Unauthorized")


AdminAuth = Depends(require_admin_token)
