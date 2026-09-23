from typing import List, Union
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    cors_origins: Union[str, List[str]] = Field(
        default="http://localhost:5173,http://127.0.0.1:5173,http://localhost:3000"
    )
    max_file_size_mb: int = Field(default=10, description="Max upload size in megabytes")
    database_url: str = Field(default="sqlite:///./resume_checker.db")
    ocr_enabled: bool = Field(default=True, description="Attempt OCR fallback for image-only PDFs")
    tesseract_cmd: str = Field(default="")
    poppler_path: str = Field(default="")
    embedding_model_name: str = Field(default="all-MiniLM-L6-v2")
    spacy_model_name: str = Field(default="en_core_web_sm")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    def get_cors_origins(self) -> List[str]:
        if isinstance(self.cors_origins, list):
            return self.cors_origins
        if isinstance(self.cors_origins, str):
            return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]
        return ["http://localhost:5173", "http://127.0.0.1:5173"]

    @property
    def max_file_size_bytes(self) -> int:
        return self.max_file_size_mb * 1024 * 1024


settings = Settings()
