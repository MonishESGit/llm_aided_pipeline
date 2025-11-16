# service/jobs.py
import uuid
from enum import Enum
from typing import Optional, Dict

class JobStatus(str, Enum):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"

class JobRecord:
    def __init__(self, job_id: str):
        self.job_id = job_id
        self.status = JobStatus.PENDING
        self.started_at: Optional[float] = None
        self.finished_at: Optional[float] = None
        self.error_message: Optional[str] = None
        self.preprocessed_df = None
        self.annotations_df = None

    @property
    def duration_seconds(self) -> Optional[float]:
        if self.started_at is not None and self.finished_at is not None:
            return self.finished_at - self.started_at
        return None

jobs: Dict[str, JobRecord] = {}

def create_job() -> JobRecord:
    job_id = str(uuid.uuid4())
    job = JobRecord(job_id)
    jobs[job_id] = job
    return job

def get_job(job_id: str) -> Optional[JobRecord]:
    return jobs.get(job_id)
