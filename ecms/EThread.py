#!/usr/bin/env python
#-*- coding: utf-8 -*-
import threading
from time import ctime,clock
import random
import sys
import os

import logging
logger=logging.getLogger('ecms')

class EThread(threading.Thread):
    def __init__(self,func,args,name='EThread'):
        threading.Thread.__init__(self) 
        self.name = name 
        self.func = func 
        self.args = args

    def run(self):
        logger.debug('starting %s at %s.' % (self.name,str(ctime())))
        try:
            self.res = apply(self.func, self.args)
            logger.debug('finished %s at %s.' % (self.name,str(ctime())))
            return self.res
        except Exception,e:
            logger.error(e)
            logger.debug('finished %s at %s.' % (self.name,str(ctime())))
            return 'error'
                    
