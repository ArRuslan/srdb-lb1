from contextlib import asynccontextmanager
from os import environ

from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from . import api, ui
from .db import DatabasePool


@asynccontextmanager
async def lifespan(_):
    db = DatabasePool(
        f"Driver=/opt/microsoft/msodbcsql18/lib64/libmsodbcsql-18.4.so.1.1;"
        f"Server=127.0.0.1;"
        f"Database=nure_lb2;"
        f"UID={environ['DB_USER']};"
        f"PWD={environ['DB_PASSWORD']};"
        f"TrustServerCertificate=yes;"
    )
    #async with db.acquire():
    #    ...  # TODO: create (if not exists) functions, procedures, etc.
    yield


app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(api.router)
app.mount("/", ui.app)
