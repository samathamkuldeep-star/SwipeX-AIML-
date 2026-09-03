from pathlib import Path

from pydantic import BaseModel

BASE_DIR = Path(__file__).resolve().parent.parent.parent
APP_DIR = BASE_DIR / "app"


class Settings(BaseModel):
    PROJECT_NAME: str = "SwipeX Career Intelligence Service"
    VERSION: str = "0.1.0"
    API_V1_STR: str = "/api/v1"

    UPLOAD_DIR: Path = BASE_DIR / "storage" / "resumes"
    MAX_FILE_SIZE_BYTES: int = 10 * 1024 * 1024
    ALLOWED_EXTENSIONS: set[str] = {".pdf", ".txt"}
    ALLOWED_MIME_TYPES: set[str] = {
        "application/pdf",
        "text/plain",
        "application/octet-stream",
    }

    DATA_DIR: Path = APP_DIR / "data"
    SEED_JOBS_FILE: Path = APP_DIR / "data" / "seed_jobs.json"

    REQUIRED_SKILLS_WEIGHT: float = 0.70
    KEYWORD_OVERLAP_WEIGHT: float = 0.30
    GENERATED_BY_TAG: str = "heuristic-v0"


settings = Settings()

settings.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
settings.DATA_DIR.mkdir(parents=True, exist_ok=True)
