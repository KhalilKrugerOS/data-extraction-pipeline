from fastapi import  APIRouter, Depends
from helpers.config import get_settings, Settings
import typing


base_router = APIRouter(
    prefix="/api/v1",
    tags=["base"]
)


@base_router.get("/")
# non-blocking. When a request is made to a route handled by an async function, the server can handle other requests concurrently while waiting for the async function to complete its execution.
# Declare a FastAPI dependency.
async def welcome(app_settings :Settings = Depends(get_settings)):
    """
    Welcome to the API.
    """
    app_name = app_settings.APP_NAME
    app_version = app_settings.APP_VERSION
    return {
        "app_name": app_name,
        "app_version": app_version
    }