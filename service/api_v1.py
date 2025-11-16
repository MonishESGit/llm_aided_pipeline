# service/api_v1.py
from fastapi import APIRouter, HTTPException
from .models import PreprocessRequest, JobStatusResponse, PreprocessResultResponse
from .jobs import create_job, get_job, JobStatus
from .logging_utils import log_event

from timeseries_preproc.pipeline import preprocess_csv

router = APIRouter(prefix="/v1")

@router.post("/jobs", response_model=JobStatusResponse)
def create_preprocess_job(req: PreprocessRequest):
    job = create_job()
    log_event("job_created", job_id=job.job_id)

    # Mark running
    job.status = JobStatus.RUNNING
    job.started_at = __import__("time").time()
    log_event("job_started", job_id=job.job_id, csv_path=req.csv_path)

    try:
        pre_df, ann_df = preprocess_csv(
            path=req.csv_path,
            smoothing_window=req.smoothing_window,
            arc_normalization=req.arc_normalization,
            min_peak_distance=req.min_peak_distance,
            min_rel_height=req.min_rel_height,
            time_index_column=req.time_index_column,
        )
        job.preprocessed_df = pre_df
        job.annotations_df = ann_df
        job.status = JobStatus.SUCCESS
        job.finished_at = __import__("time").time()
        log_event(
            "job_completed",
            job_id=job.job_id,
            duration=job.duration_seconds,
            n_curves=pre_df.shape[1],
        )
    except Exception as e:
        job.status = JobStatus.FAILED
        job.finished_at = __import__("time").time()
        job.error_message = str(e)
        log_event("job_failed", job_id=job.job_id, error=str(e))
        raise HTTPException(status_code=500, detail="Job failed")

    return JobStatusResponse(
        job_id=job.job_id,
        status=job.status,
        started_at=str(job.started_at),
        finished_at=str(job.finished_at),
        duration_seconds=job.duration_seconds,
        error_message=job.error_message,
    )

@router.get("/jobs/{job_id}", response_model=JobStatusResponse)
def get_job_status(job_id: str):
    job = get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return JobStatusResponse(
        job_id=job.job_id,
        status=job.status,
        started_at=str(job.started_at),
        finished_at=str(job.finished_at),
        duration_seconds=job.duration_seconds,
        error_message=job.error_message,
    )

@router.get("/jobs/{job_id}/results", response_model=PreprocessResultResponse)
def get_job_results(job_id: str):
    job = get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    if job.status != JobStatus.SUCCESS:
        raise HTTPException(status_code=400, detail=f"Job not successful: {job.status}")
    # For responses, send only head() to keep JSON small
    pre_head = job.preprocessed_df.to_dict(orient="records")
    ann_head = job.annotations_df.to_dict(orient="records")
    return PreprocessResultResponse(
        job_id=job.job_id,
        status=job.status,
        preprocessed_head=pre_head,
        annotations_head=ann_head,
    )
