from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    APP_NAME: str
    APP_VERSION: str
    OPENAI_API_KEY: str
    File_ALLOWED_EXTENSIONS: str
    File_Max_SIZE: int
    FILE_DEFAULT_CHUCK_SIZE: int

    model_config = SettingsConfigDict(
        env_file=".env", 
        env_file_encoding="utf-8"
    )


def get_settings() -> Settings:
    return Settings()
