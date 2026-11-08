import time
from app.celery_app import celery_app

@celery_app.task(
    bind=True,
    name="app.tasks.process_report",
    max_retries=3
)
#decorator turns a regular python function into a celery background task
#bind=true passes the task instance itself 
#name=explicitly registers the unique name for task in the broker queue
#use=ensures that even if u refactor or move your python files around celery workers correctly match incoming queue messages to this exact function name
#max_retries=3
#What it does: Sets a safety limit on how many times Celery is allowed to re-attempt this task if it crashes or fails.

#Why it's used: Prevents a broken task from looping infinitely forever and clogging up your server resources.
def process_report(
    self,
    report_text:str,
    simulate_failure:bool=False
):
    '''self: The bound task instance (enabled by bind=True above). Used here to check retry counts and trigger error handling.

report_text: str: The actual data payload passed into the task (e.g., the text content of the report you want to process).

simulate_failure: bool = False: A handy testing switch. If set to True, it forces the task to intentionally fail first so you can test if Celery's automatic retry logic works correctly.'''
    time.sleep(30)
    if simulate_failure and self.request.retries<2:
        raise self.retry(
            exc=RuntimeError("Temporary Processing Failure"),
            countdown=2,
        )
    words = report_text.split()

    return {
        "message": "Report processed successfully",
        "word_count": len(words),
        "character_count": len(report_text),
        "attempts": self.request.retries + 1,
    }