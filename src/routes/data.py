from fastapi import APIRouter, Depends, UploadFile, status, Request
from fastapi.responses import JSONResponse
import aiofiles
from helpers.config import get_settings, Settings
from controllers import DataController, ProcessController
import logging

from models.ChunkModel import ChunkModel
from models.db_schemes.data_chunk import DataChunk
from models.db_schemes.project import Project
from models.enums import RESPONSES
from .schemes.data import ProcessRequest
from models.ProjectModel import ProjectModel


logger = logging.getLogger("uvicorn.error")

data_router = APIRouter(prefix="/api/v1/data", tags=["api_v1", "data"])


@data_router.post("/upload/{project_id}")
async def upload_data(
    request: Request,
    project_id: str,
    file: UploadFile,
    app_settings: Settings = Depends(get_settings),
):
    
    project_model = ProjectModel(db_client=request.app.db_client)
    project = await project_model.get_project_or_create_one(project_id=project_id)


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
    file_path, file_id = data_controller.generate_unique_filepath(
        file.filename, project_id=project_id
    )
    # write the file to disk
    # use aiofiles to write the file asynchronously
    # handle issues without exposing the user to the error
    try:
        async with aiofiles.open(file_path, "wb") as f:
            while chunk := await file.read(app_settings.FILE_DEFAULT_CHUNK_SIZE):
                await f.write(chunk)
    except Exception as e:
        logger.error(
            f"Error while writing file {file.filename} to disk: {file_path} because {e}"
        )
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "signal": ResponseSignal.FILE_UPLOAD_FAILED.value},
        )
 
    return JSONResponse(
        status_code=status.HTTP_200_OK, content={
            "signal": signal.value,
            "file_id": file_id,
            "project_id": str(project.id),
            }
    )

@data_router.post("/process/{project_id}")
async def process_endpoint(request: Request, project_id: str, process_request: ProcessRequest):
    file_id = process_request.file_id
    chunk_size = process_request.chunk_size or 100
    overlap_size = process_request.overlap_size or 20
    do_reset = process_request.do_reset or 0

    project_model = ProjectModel(db_client=request.app.db_client)
    chunk_model = ChunkModel(db_client=request.app.db_client)


    project = await project_model.get_project_or_create_one(project_id=project_id)

    process_controller = ProcessController(project_id=project_id)
    file_content = process_controller.get_file_content(file_id=file_id)

    if file_content is None:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"signal": RESPONSES.ResponseSignal.FILE_NOT_FOUND.value},
        )
    
    chunked_content = process_controller.process_file(
        file_id=file_id,
        file_content=file_content,
        chunck_size=chunk_size,
        overlap_size=overlap_size
    )
    # chouf if chunked content is empty return error
    if chunked_content is None or len(chunked_content) == 0:
         return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"signal": RESPONSES.ResponseSignal.FILE_PROCESSING_FAILED.value},
        )
    
    if do_reset == 1:
        # delete all the chunks for the project
        logger.info(f"Deleting all chunks for project {str(project.id)}")
        deleted_count = await chunk_model.delete_chunks_by_project_id(project_id=project.id)
        logger.info(f"Deleted {deleted_count} chunks for project {project_id}")
    
    # save the chunks to the database
    file_chunks_records = [
        DataChunk(
            chunk_text=chunk.page_content,
            chunk_metadata=chunk.metadata,
            chunk_order=i + 1,
            chunk_project_id=project.id,
        )
        for i, chunk in enumerate(chunked_content)
    ]

    no_chunks = await chunk_model.insert_many_chunks(chunks=file_chunks_records)
    return no_chunks

