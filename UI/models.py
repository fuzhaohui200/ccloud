# -*- coding: utf-8 -*-
from django.db import models
import datetime
import logging
logger=logging.getLogger('ecms')


class Notice(models.Model):
    title=models.CharField(max_length=100)
    content=models.TextField(max_length=2000)
    pub_date=models.DateTimeField()
    
    def __unicode__(self):
        return '%s' % (self.title)
    
    
    def save(self,*args,**kwargs):
        if not self.id:
            self.pub_date=datetime.datetime.today()
        return super(Notice,self).save(*args,**kwargs)
        
