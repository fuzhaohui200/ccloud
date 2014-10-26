
import traceback
import sys

from apscheduler.scheduler import Scheduler
sched=Scheduler()
sched.start()

def trace_back():
    try:
        return traceback.format_exc()
    except:
        return 'trace back error.'