from contextlib import asynccontextmanager
from fastapi import FastAPI
from helpers.config import get_settings
from routes import base, data
from motor.motor_asyncio import AsyncIOMotorClient


## old way of doing it
"""
@app.on_event("startup")
async def startup_event():
    settings = get_settings()
    app.mongo_conn = AsyncIOMotorClient(settings.MONGO_URI)
    app.db_client = app.mongo_conn[settings.MONGO_DATABASE]


@app.on_event("shutdown")
async def shutdown_event():
    app.mongo_conn.close()
    """


## recommended way of doing it
@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    app.mongo_conn = AsyncIOMotorClient(settings.MONGO_URI) # type: ignore
    app.db_client = app.mongo_conn[settings.MONGO_DATABASE]# type: ignore
    yield
    app.mongo_conn.close()# type: ignore

app = FastAPI(lifespan=lifespan)

app.include_router(base.base_router)
app.include_router(data.data_router)
