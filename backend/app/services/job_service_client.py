import json
from pathlib import Path

from backend.app.core.config import settings
from backend.app.models.schemas import JobDetail


class JobServiceClient:
    def __init__(self, seed_file: Path = settings.SEED_JOBS_FILE):
        self.seed_file = seed_file
        self._cached_jobs: dict[str, JobDetail] = {}
        self._load_seed_jobs()

    def _load_seed_jobs(self) -> None:
        if not self.seed_file.exists():
            return

        try:
            with open(self.seed_file, encoding="utf-8") as f:
                data = json.load(f)
                for item in data:
                    job = JobDetail(**item)
                    self._cached_jobs[job.job_id] = job
        except Exception as e:
            print(f"[Warning] Failed to load seed jobs: {e}")

    def get_job(self, job_id: str) -> JobDetail | None:
        return self._cached_jobs.get(job_id)

    def list_jobs(self) -> list[JobDetail]:
        return list(self._cached_jobs.values())

    def add_or_update_job(self, job: JobDetail) -> None:
        self._cached_jobs[job.job_id] = job


job_service_client = JobServiceClient()
