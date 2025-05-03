from venv import logger
from .BaseController import BaseController
from .ProjectController import ProjectController
from models import ProcessingEnum

import os

from langchain_community.document_loaders import TextLoader, PyMuPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

class ProcessController(BaseController):
    def __init__(self, project_id: str):
        super().__init__();
        self.project_id = project_id
        self.project_path = ProjectController().get_project_path(project_id)

    def get_file_extension(self, file_id: str):
        return os.path.splitext(file_id)[-1]
    
    def get_file_loader(self, file_id: str):

        file_extension = self.get_file_extension(file_id=file_id)
        # file id under project path
        file_path = os.path.join(self.project_path, file_id)
        # check if file exists
        if not os.path.exists(file_path):
            logger.warning(
                f"File {file_path} does not exist for file id {file_id}"
            )
            return None
        if file_extension == ProcessingEnum.TXT.value:
            return TextLoader(file_path=file_path, encoding="utf-8")
        
        if file_extension == ProcessingEnum.PDF.value:
            return PyMuPDFLoader(file_path=file_path)
        # only support pdf and txt for now
        logger.warning(
            f"File type {file_extension} is not supported for file id {file_id}"
        )
        return None
    
    def get_file_content(self, file_id: str):
        loader = self.get_file_loader(file_id=file_id)
        if loader is None:
            return None
        documents = loader.load()
        return documents

    def process_file(self, file_id: str,
                        file_content: list, chunck_size: int = 100,
                        overlap_size: int = 20
                    ):

        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunck_size,
            chunk_overlap=overlap_size,
            length_function=len,
        )

        file_content_text = [
            rec.page_content 
            for rec in file_content
        ]

        file_content_metadata = [
            rec.metadata 
            for rec in file_content
        ]

        chunks = text_splitter.create_documents(
            texts=file_content_text,
            metadatas=file_content_metadata
        )
        return chunks