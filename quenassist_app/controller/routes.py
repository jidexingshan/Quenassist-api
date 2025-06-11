from fastapi import APIRouter, FastAPI

from . import views


def init_routers(app: FastAPI):
    app.include_router(views.router, prefix="/api/v1", tags=["v1"])
