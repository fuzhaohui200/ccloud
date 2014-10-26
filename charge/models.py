# -*- coding: utf-8 -*-
from django.db import models

# Create your models here.

import logging
logger=logging.getLogger('ecms')

from ecms.commonfunction import *

class vioclient_usage_log(models.Model):
    vioclient_user=models.CharField(max_length=50)
    vioclient_name=models.CharField(max_length=50)
    vioclient_cpu=models.IntegerField()
    vioclient_mem=models.IntegerField()
    use_days=models.IntegerField()
    start_date=models.DateField()
    end_date=models.DateField(blank=True,null=True)
    
    def __unicode__(self):
        return 'User: %s, vioclient: %s, Used_Days: %d' % (self.vioclient_user,self.vioclient_name,self.use_days)
    
    
