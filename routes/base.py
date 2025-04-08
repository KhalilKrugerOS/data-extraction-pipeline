from fastapi import FastAPI, APIRouter
import os

base_router = APIRouter(
    prefix="/api/v1",
    tags=["base"]
)


@base_router.get("/")
# non-blocking. When a request is made to a route handled by an async function, the server can handle other requests concurrently while waiting for the async function to complete its execution.
async def welcome():
    """
    Welcome to the API.
    """
    return {
        "message": f"Runnig {os.getenv("APP_NAME")}:{os.getenv('APP_VERSION')}"
    }