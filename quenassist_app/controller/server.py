import uvicorn
from fastapi import FastAPI

from quenassist_app.config import settings
from . import middlewares, routes
from quenassist_app.system.log import init_log


class Server:
    def __init__(self):
        self.app = FastAPI()

    def init_app(self):
        routes.init_routers(self.app)
        middlewares.init_middleware(self.app)

    def run(self):
        self.init_app()
        uvicorn.run(app=self.app, host=settings.HOST, port=settings.PORT)
