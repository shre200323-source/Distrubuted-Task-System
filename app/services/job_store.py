from app.redis_client import redis_client
def set_job_status(job_id:str,status:str):
    key=f"app:job:{job_id}:status"
    redis_client.set(
        key,
        status,
        ex=3600
    )

def get_job(job_id:str):
    key=f"app:job:{job_id}:status"
    return redis_client.get(key)

def increment_total_jobs():
    return redis_client.incr("app:job:total")

def delete_job_status(job_id:str):
    key = f"app:job:{job_id}:status"
    return redis_client.delete(key)

def create_all_job(job_id:str,report_text:str,status:str,priority:int,simulate_failure:bool):
    key=f"app:job:{job_id}"
    redis_client.hset(
        key,
        mapping={
            "job_id":job_id,
            "report_text":report_text,
            "simulate_failure":str(simulate_failure),
            "status":status,
            "priority":priority
        }
    )
    redis_client.expire(key,3600)


def get_job(job_id:str):
    key=f"app:job:{job_id}"
    job=redis_client.hgetall(key)
    return job if job else None


def update_job_status(job_id:str,status:str):
    key=f"app:job:{job_id}"
    redis_client.hset(key,"status",status)

