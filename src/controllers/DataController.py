from fastapi import UploadFile
from .BaseController import BaseController
from models import ResponseSignal
from .ProjectController import ProjectController
import re
import os


# datacontroller is a baseController
# logic handlinf for the /data endpoint
class DataController(BaseController):
    def __init__(self):
        super().__init__()
        self.convertMBtoBytes: int = 1024 * 1024

    def validate_uploaded_file(self, uploaded_file: UploadFile):
        if (
            uploaded_file.content_type is None
            or uploaded_file.content_type
            not in self.app_settings.File_ALLOWED_EXTENSIONS
        ):
            return False, ResponseSignal.FILE_VALIDATION_FAILED_FILE_TYPE
        elif uploaded_file.size is None or (
            uploaded_file.size
            > (self.app_settings.File_Max_SIZE * self.convertMBtoBytes)
        ):
            return False, ResponseSignal.FILE_VALIDATION_FAILED_FILE_SIZE
        return True, ResponseSignal.FILE_UPLOAD_SUCCESS

    def generate_unique_filename(self, orig_filename: str, project_id: str):
        random_key = self.generate_random_string()
        project_path = ProjectController().get_project_path(project_id=project_id)
        cleaned_filename = self.get_clean_filename(orig_filename)
        new_file_path = os.path.join(project_path, random_key + "_" + cleaned_filename)
        while os.path.exists(new_file_path):
            random_key = self.generate_random_string()
            new_file_path = os.path.join(
                project_path, random_key + "_" + cleaned_filename
            )
        return new_file_path

    def get_clean_filename(self, orig_filename: str):
        # Remove any special characters from the filename
        cleaned_filename = re.sub(r"[^\w.]", "", orig_filename.strip())

        cleaned_filename = cleaned_filename.replace(" ", "_")

        return cleaned_filename
