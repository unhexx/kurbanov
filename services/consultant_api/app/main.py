from fastapi import FastAPI

from app.routers import admin, telegram
from app.web.router import mount_web


def create_app() -> FastAPI:
    app = FastAPI(title="Consultant API", version="0.1.0")
    # Веб-интерфейс монтируется первым: HTML-страницы и формы имеют
    # приоритет над JSON-эндпоинтами при пересечении путей под /admin.
    mount_web(app)
    app.include_router(telegram.router)
    app.include_router(admin.router)
    return app


app = create_app()
