from fastapi import FastAPI, APIRouter, Depends, UploadFile, status
from fastapi.responses import JSONResponse
import os 
import aiofiles
from helpers.config import get_settings, Settings
from controllers import DataController, ProjectController


data_router = APIRouter(
    prefix="/api/v1/data",
    tags=["api_v1", "data"]
)

@data_router.post("/upload/{project_id}")
async def upload_data(project_id: str, file: UploadFile,
                       app_settings :Settings = Depends(get_settings)):
    # validate the file properties
    # logic in controller.Datacontroller
    is_valid, signal = DataController().validate_uploaded_file(file)
    
    if not is_valid:
        return JSONResponse(
            status_code= status.HTTP_400_BAD_REQUEST,
            content={
                "signal": signal.value
            }
        )
    
    # save the file
    project_dir_path = ProjectController().get_project_path(project_id=project_id)
    file_path = os.path.join(project_dir_path, file.filename)
    async with aiofiles.open(file_path, "wb") as f:
        while chunk := await file.read(app_settings.FILE_DEFAULT_CHUCK_SIZE):
            await f.write(chunk)

    return JSONResponse(
            content={
                "signal": signal.value
            }
        )