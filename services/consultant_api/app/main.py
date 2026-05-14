from fastapi import FastAPI

from app.routers import admin, telegram


def create_app() -> FastAPI:
    app = FastAPI(title="Consultant API", version="0.1.0")
    app.include_router(telegram.router)
    app.include_router(admin.router)
    return app


app = create_app()

