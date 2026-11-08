import os 
import redis
from app.config import REDIS_URL
REDIS_URL=os.getenv(
    "REDIS_URL",
     REDIS_URL
)

redis_client=redis.Redis.from_url(
    REDIS_URL,
    decode_responses=True
)

def check_redis_connection():
    try:
        return redis.client.ping()
    except redis.RedisError as error:
        print(f"Redis connection error:{error}")
        return False


def add_job_to_history(job_id:str):
    key="app:job:history"
    redis_client.lpush(key,job_id)
    redis_client.ltrim(key,0,99)

def get_job_history():
    key="app:job:histroy"
    redis_client.lrange(key,0,-1)


def get_job_history_count():
    key="app:job:history"
    redis_client.llen(key)

def add_jobs_to_priority_queue(job_id:str,priority:int):
    key="app:job:priority"
    redis_client.zadd(
        key,
        {job_id:priority}
    )



