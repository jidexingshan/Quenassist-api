from typing import Callable

from fastapi import FastAPI, Request, Response

from quenassist_app.service.mysql.mysql_db import SessionFactory
from fastapi.middleware.cors import CORSMiddleware

origins = [
    "http://192.168.2.9:3000",
    "http://localhost",
    "http://localhost:8000",
    "http://localhost:3000"
]

async def db_session_middleware(request: Request, call_next: Callable) -> Response:
    response = Response('Internal server error', status_code=500)
    try:
        request.state.db = SessionFactory()
        response = await call_next(request)
    finally:
        request.state.db.close()

    return response


def init_middleware(app: FastAPI) -> None:
    app.middleware('http')(db_session_middleware)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"], # origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )