from app.redis_client import redis_client
from app.services.job_store import get_job,update_job_status
from app.tasks import process_report

def dispatch_next_job():
    result=redis_client.zpopmax("app:job:priority")
    if not result:
        return {"message":"No jobs waiting for priority queue"}

    job_id,priority=result[0]
    job = get_job(job_id=job_id)
    if not job:
        return {
            "job_id":job_id,
            "message":"Job details not found"
        }

    simulate_failure = (
    job.get("simulate_failure", "false").lower() == "true"
)

    try:
        task = process_report.apply_async(
            args=[
                job["report_text"],
                simulate_failure
            ],
            task_id=job_id,
        )

        update_job_status(job_id,"QUEUED")

        return {
            "job_id":job_id,
            "priority":priority,
            "celery_task_id":task.id,
            "status":"QUEUED",
            "message":"Job_successfully dipatched to Celery"
        }
    except Exception:
        redis_client.zadd(
            "app:job:priority",
            {job_id:priority},
        )
        update_job_status(job_id,"WAITING")
        raise