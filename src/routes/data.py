from fastapi import APIRouter, Depends, UploadFile, status
from fastapi.responses import JSONResponse
import aiofiles
from helpers.config import get_settings, Settings
from controllers import DataController
from models.enums import RESPONSES
import logging


logger = logging.getLogger("uvicorn.error")

data_router = APIRouter(prefix="/api/v1/data", tags=["api_v1", "data"])


@data_router.post("/upload/{project_id}")
async def upload_data(
    project_id: str,
    file: UploadFile,
    app_settings: Settings = Depends(get_settings),
):
    # validate the file properties
    # logic in controller.DataController
    ResponseSignal = RESPONSES.ResponseSignal
    data_controller = DataController()
    is_valid, signal = data_controller.validate_uploaded_file(file)

    if not is_valid:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"signal": signal.value},
        )

    # save the file
    # project_dir_path = ProjectController().get_project_path(project_id=project_id)
    if not file.filename:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"signal": "Invalid file: filename is missing"},
        )
    file_path = data_controller.generate_unique_filename(
        file.filename, project_id=project_id
    )
    # write the file to disk
    # use aiofiles to write the file asynchronously
    # handle issues without exposing the user to the error
    try:
        async with aiofiles.open(file_path, "wb") as f:
            while chunk := await file.read(app_settings.FILE_DEFAULT_CHUCK_SIZE):
                await f.write(chunk)
    except Exception as e:
        logger.error(
            f"Error while writing file {file.filename} to disk: {file_path} because {e}"
        )
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"signal": ResponseSignal.FILE_UPLOAD_FAILED.value},
        )
    return JSONResponse(
        status_code=status.HTTP_200_OK, content={"signal": signal.value}
    )
