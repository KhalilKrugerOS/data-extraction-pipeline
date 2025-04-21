from fastapi import UploadFile
from .BaseController import BaseController
from models import ResponseSignal


# datacontroller is a baseController
# logic handlinf for the /data endpoint
class DataController(BaseController):

    def __init__(self):
        super().__init__()
        self.convertMBtoBytes: int = 1024*1024

    def validate_uploaded_file(self, uploaded_file: UploadFile):
        if uploaded_file.content_type is None or \
            uploaded_file.content_type not in \
                self.app_settings.File_ALLOWED_EXTENSIONS:
            return False, ResponseSignal.FILE_VALIDATION_FAILED_FILE_TYPE
        elif uploaded_file.size is None or (
            uploaded_file.size >
                (self.app_settings.File_Max_SIZE * self.convertMBtoBytes)):
            return False, ResponseSignal.FILE_VALIDATION_FAILED_FILE_SIZE
        return True, ResponseSignal.FILE_UPLOAD_SUCCESS
