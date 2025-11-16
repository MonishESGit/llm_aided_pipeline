# service/api_v2.py
from fastapi import APIRouter, HTTPException
from .models import PreprocessRequest, PreprocessResultResponse
from .jobs import create_job, JobStatus
from .logging_utils import log_event
from timeseries_preproc.pipeline import preprocess_csv

router = APIRouter(prefix="/v2")

# For brevity, we’ll only define a “synchronous” endpoint that directly returns results

@router.post("/preprocess", response_model=PreprocessResultResponse)
def preprocess_sync(req: PreprocessRequest):
    job = create_job()
    log_event("job_created_v2", job_id=job.job_id)

    job.status = JobStatus.RUNNING
    job.started_at = __import__("time").time()
    log_event("job_started_v2", job_id=job.job_id, csv_path=req.csv_path)

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
    except Exception as e:
        job.status = JobStatus.FAILED
        job.finished_at = __import__("time").time()
        job.error_message = str(e)
        log_event("job_failed_v2", job_id=job.job_id, error=str(e))
        raise HTTPException(status_code=500, detail="Job failed")

    pre_head = job.preprocessed_df.to_dict(orient="records")
    ann_head = job.annotations_df.to_dict(orient="records")

    return PreprocessResultResponse(
        job_id=job.job_id,
        status=job.status,
        preprocessed_head=pre_head,
        annotations_head=ann_head,
    )
