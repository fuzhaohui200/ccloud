import EUAO.models
import logging
logger=logging.getLogger('ecms')

from apscheduler.scheduler import Scheduler
from datetime import date
import datetime
import suds
from time import sleep
sched=Scheduler()
sched.start()
from ecms.commonfunction import *

def _run(task):
    space=task.task_space
    function_name=task.function.name
    webservice=suds.client.Client(space.url)
    function_str='webservice.service.%s(%s)' % (function_name,task.parameters)
    logger.debug('euao function str: %s' % function_str)
    try:
        thread_id=eval(function_str)
        logger.debug('euao thread: %s' % thread_id)
        if thread_id:
            task.euao_thread_id=thread_id
            task_executing=EUAO.models.task_status.objects.get(name='executing')
            task.status=task_executing
            task.save()
        else:
            logger.error('Error in executing euao task.')
    except Exception,e:
        logger.error('Error in calling EUAO. %s' % e)
        logger.debug(trace_back())
        task.status=EUAO.models.task_status.objects.get(name='error')
        
def run_task(task):
    if task.plan_execute_time==None or task.plan_execute_time=='':
        #run immediately
        _run(task)
        
def run_check_task(check_task_item):
    space=check_task_item.task_space
    function_name=check_task_item.function
    webservice=suds.client.Client(space.url)
    function_str='webservice.service.%s(%s)' % (function_name,check_task_item.parameters)
    logger.debug('euao function str: %s' % function_str)
    
    try:
        thread_id=eval(function_str)
        logger.debug('euao thread: %s' % thread_id)
        if thread_id:
            check_task_item.euao_thread_id=thread_id
            task_executing=EUAO.models.task_status.objects.get(name='executing')
            check_task_item.status=task_executing
            check_task_item.save()
        else:
            logger.error('Error in executing euao task.')
    except Exception,e:
        logger.error('Error in calling EUAO. %s' % e)
        check_task_item.status=EUAO.models.task_status.objects.get(name='error')

#sucks, need a new thread to do this
def GetResponse(task_item,retry_count):
    space=task_item.task_space
    webservice=suds.client.Client(space.url)
    function_str="""webservice.service.GetCommandResponse('%s')""" % task_item.euao_thread_id
    try:
        not_finished=True
        try_count=0
        while not_finished and try_count<retry_count:
            output_t,exit_code_t=eval(function_str)
            output=output_t[1]
            exit_code=exit_code_t[1]
            logger.debug('output: %s, exit_code: %d' % (output,exit_code))
            if exit_code==2:#running
                try_count+=1
                sleep(10)
            elif exit_code==0:# finished
                finished_status=EUAO.models.task_status.objects.get(name='finished')
                task_item.status=finished_status
                task_item.result=output
                logger.debug('Task: %s, exit_code: %d, output: %s' % (task_item,exit_code,output))
                task_item.save()
                not_finished=False
            else:
                error_status=EUAO.models.task_status.objects.get(name='error')
                logger.debug('Task: %s, exit_code: %d, output: %s' % (task_item,exit_code,output))
                task_item.status=error_status
                task_item.result=output
                task_item.save()
                not_finished=False
        
        if try_count==retry_count:
            error_status=EUAO.models.task_status.objects.get(name='error')
            logger.info('Task %s timeout for %d seconds.' % (task_item,try_count*10))
            logger.debug('Task: %s, exit_code: %d, output: %s' % (task_item,exit_code,output))
            task_item.status=error_status
            task_item.result=output
            task_item.save()
            not_finished=False
            
        
            
    except Exception,e:
        logger.error('Error in Get %s response. %s' % (task_item,e))
        logger.debug(trace_back())
        error_status=EUAO.models.task_status.objects.get(name='error')
        logger.debug('Task: %s, exit_code: %d, output: %s' % (task_item,exit_code,output))
        task_item.status=error_status
        task_item.result=output
        task_item.save()
   
def run_job_interval_times(job_name,job_parameter,interval_seconds,times):
    now_time=datetime.datetime.now()
    timedelta=datetime.timedelta(seconds=interval_seconds)
    jobs=[]
    for i in range(times):
        job=sched.add_date_job(job_name,now_time+i*timedelta,job_parameter)
        jobs.append(job)
    return jobs

def reset_all():
    test_delete_euao_check_task()
    test_delete_euao_task()

def test_delete_euao_task():
    euao_tasks=EUAO.models.task.objects.all()
    for et in euao_tasks:
        et.delete()
        
def test_delete_euao_check_task():
    euao_check_tasks=EUAO.models.check_task.objects.all()
    for ect in euao_check_tasks:
        ect.delete()
