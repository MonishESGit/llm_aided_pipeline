# service/models.py
from pydantic import BaseModel
from typing import Optional, List, Dict, Any

class PreprocessRequest(BaseModel):
    csv_path: str                 # or later: can be replaced by file upload
    smoothing_window: int = 5
    smoothing_center: bool = True
    arc_normalization: bool = False
    min_peak_distance: int = 5
    min_rel_height: float = 0.1
    time_index_column: Optional[str] = None

class JobStatusResponse(BaseModel):
    job_id: str
    status: str                   # "PENDING", "RUNNING", "SUCCESS", "FAILED"
    started_at: Optional[str] = None
    finished_at: Optional[str] = None
    duration_seconds: Optional[float] = None
    error_message: Optional[str] = None

class PreprocessResultResponse(BaseModel):
    job_id: str
    status: str
    preprocessed_head: List[Dict[str, Any]]
    annotations_head: List[Dict[str, Any]]
