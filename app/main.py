
from fastapi import FastAPI
from pydantic import BaseModel, Field
import uuid
from app.celery_app import celery_app
from app.tasks import process_report
from app.dispatcher import dispatch_next_job
from app.services.job_store import (set_job_status,get_job,increment_total_jobs,create_all_job,update_job_status)
from app.redis_client import (add_job_to_history,get_job_history,get_job_history_count,add_jobs_to_priority_queue)
app = FastAPI(
    title="Distributed Task Processing API",
    version="1.0.0",
)


class JobRequest(BaseModel):
    report_text: str = Field(
        min_length=1,
        max_length=10000,
    )
    simulate_failure: bool = False
    priority:int=Field(default=5,ge=1,le=10)


@app.get("/")
def health_check():
    return {"message": "API is running"}


@app.post("/jobs", status_code=202)
def create_job(request: JobRequest):

    job_id=str(uuid.uuid4())
    create_all_job(job_id=job_id,report_text=request.report_text,status="PENDING",priority=request.priority,simulate_failure=request.simulate_failure)
    #set_job_status(job_id=task.id,status="PENDING")
    add_jobs_to_priority_queue(job_id=job_id,priority=request.priority)
    add_job_to_history(job_id)
    increment_total_jobs()
    return {
        "task_id": job_id,
        "status": "PENDING",
        "message": "Job submitted successfully",
    }


@app.get("/jobs/{task_id}")
def get_job_status(task_id: str):

    job = get_job(task_id)

    if not job:
        return {"message": "Job not found"}

    task = celery_app.AsyncResult(task_id)

    update_job_status(task_id, task.state)

    job["status"] = task.state

    if task.successful():
        job["result"] = task.result

    elif task.failed():
        job["error"] = str(task.result)

    return job

@app.get("/get_job_history")
def app_get_job_histroy():
    job_ids=get_job_history()
    return {
        "total_jobs":get_job_history_count,
        "job_histroy":job_ids,
    }

@app.post("/job/dispatch_next_job")
def app_dispatch_next_job():
    return dispatch_next_job()