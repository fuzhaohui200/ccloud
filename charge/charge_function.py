# -*- coding: utf-8 -*-
from ecms.EThread import EThread
import logging
logger=logging.getLogger('ecms')
import EUAO
import ecms.commonfunction
import time
from ecms.commonfunction import *
from models import vioclient_usage_log

def test_clear_all_vioclient_log():
    for item in vioclient_usage_log.objects.all():
        item.delete()
        

def calcharge():
    try:
        #add one to days for eath vioclient_usage_log
        logger.debug('=============== cron job: Add 1 day to all used vioclient =====')
        for item in vioclient_usage_log.objects.filter(end_date__isnull=True):
                #no end_date, this vioclient is still in used.
                logger.debug('Add 1 day to %s' % item.vioclient_name)        
                item.use_days+=1
                item.save()
        logger.debug('=============== cron job end ==================================')
    except Exception,e:
        logger.error('cronjob error:%s' % e)
        logger.debug(trace_back())

def add_to_sche():
    #cal charge every day at 00:00
    ecms.commonfunction.sched.add_cron_job(calcharge,hour='0')