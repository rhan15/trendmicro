from apscheduler.schedulers.background import BackgroundScheduler
from app.Routes.spread_dt9 import *
from pytz import timezone

scheduler = BackgroundScheduler(timezone="Asia/Jakarta")

def init_scheduler(app):

    scheduler = BackgroundScheduler(timezone=timezone("Asia/Jakarta"))
    
    scheduler.add_job(
        proced_spread_dt9,
        trigger="cron",
        hour="*/2",   # tiap 2 jam
        minute="0",   # menit ke 00
        id="JOB_SPREAD_DT9",
        replace_existing=True,
        misfire_grace_time=3000
    )


    if not scheduler.running:
        scheduler.start()
        print("============================= LIST SCHEDULED JOB =============================")
        for job in scheduler.get_jobs():
            print(job.id, job.next_run_time)

        print("\n")


