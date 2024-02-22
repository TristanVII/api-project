from apscheduler.schedulers.background import BackgroundScheduler

from load_configs import load_log_conf

LOGGER = load_log_conf()


def init_scheduler(func, time):
    sched = BackgroundScheduler(daemon=True)
    sched.add_job(func,
                  'interval',
                  seconds=time)
    sched.start()
    LOGGER.info("Started Periodic Processing...")
