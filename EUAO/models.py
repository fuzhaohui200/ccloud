from django.db import models

from django.db.models.signals import *
from django.dispatch import receiver

from django.contrib.auth.models import User
from apscheduler.scheduler import Scheduler

from EUAO.euao_function import *
import workflow.models
import workflow.description as workflow_description
import aix
from ecms.EThread import EThread
from ecms.commonfunction import *
import logging
logger=logging.getLogger('ecms')

sched=Scheduler()

# Create your models here.

class euao_service_space(models.Model):
    name=models.CharField(max_length=50)
    url=models.URLField()
    def __unicode__(self):
        return self.name

class euao_service_function(models.Model):
    space=models.ForeignKey(euao_service_space)
    name=models.CharField(max_length=50)
    
    def __unicode__(self):
        return "%s %s" % (self.space.name,self.name)

class task_status(models.Model):
    #pending,running,fail,success
    name=models.CharField(max_length=50)
    
    def __unicode__(self):
        return self.name
    

class check_task(models.Model):
    #euao check task
    task_space=models.ForeignKey(euao_service_space)
    function=models.ForeignKey(euao_service_function)
    task_id=models.IntegerField()
    parameters=models.TextField(max_length=50000,blank=True,null=True)
    euao_thread_id=models.CharField(max_length=100,blank=True,null=True)
    status=models.ForeignKey(task_status)
    result=models.TextField(max_length=50000,blank=True,null=True)
    verdict_condition=models.CharField(max_length=300)
    
    def __unicode__(self):
        return "ID: %d, Service reqeust id: %d, function: %s, status: %s." % \
                    (self.id,self.service_request_id,self.function.name,self.status.name)


class target_type(models.Model):
    name=models.CharField(max_length=50)
    
    def __unicode__(self):
        return 'type: %s' % self.name

class task(models.Model):
    #EUAO task
    service_request_id=models.IntegerField()
    task_space=models.ForeignKey(euao_service_space)
    function=models.ForeignKey(euao_service_function)
    parameters=models.TextField(max_length=50000,blank=True,null=True)
    estimated_execute_time=models.IntegerField(blank=True,null=True)
    plan_execute_time=models.DateTimeField(blank=True,null=True)
    euao_thread_id=models.CharField(max_length=100,blank=True,null=True)
    follow_up_task_id=models.IntegerField(blank=True,null=True)
    check_task=models.ForeignKey(check_task,blank=True,null=True)
    status=models.ForeignKey(task_status)
    result=models.TextField(max_length=50000,blank=True,null=True)
    target_type=models.ForeignKey(target_type,blank=True,null=True)
    target_instance_number=models.IntegerField(blank=True,null=True)
    
    def __unicode__(self):
        return "ID: %d, Service reqeust id: %d, function: %s, status: %s." % \
                    (self.id,self.service_request_id,self.function.name,self.status.name)
    
    
    def set_succeed_result(self):
        if self.target_type:
            if self.target_type.name=='aix_vioclient' and self.function.name=='InstallWholeAIX':
                m_vioclient=aix.models.vioclient.objects.get(id=self.target_instance_number)
                vioclient_normal_status=aix.models.vioclient_status.objects.get(status_id=5)
                m_vioclient.status=vioclient_normal_status
                m_vioclient.save()
            if self.target_type.name=='aix_vioclient':
                if self.function.name=='RemoveWholeAIX':
                    #free the lock resource
                    try:
                        vioclient_item=aix.models.vioclient.objects.get(id=self.target_instance_number)
                        aix_resouce_lock_item=vioclient_item.resource_lock_item
                        aix_resource_lock_free_status=aix.models.aix_resource_lock_status.objects.get(status='free')
                        aix_resouce_lock_item.status=aix_resource_lock_free_status
                        aix_resouce_lock_item.save()
                        aix_resouce_lock_item.delete()
                        vioclient_item.delete()
                        
                        username=vioclient_item.belong_to_username
                        user=User.objects.get(username=username)
                        user_profile=user.get_profile()
                        user_profile.aix_cpu_used-=vioclient_item.desired_procs
                        user_profile.aix_mem_used-=vioclient_item.desired_mem
                        user_profile.aix_count_used-=1
                        user_profile.save()
                        
                    except Exception,e:
                        logger.error('Error in delete vioclient:%s' % e)
                        logger.debug(trace_back())
                elif self.function.name=='RestartVIOClient' or self.function.name=='StartVIOClient':
                    #mark the vioclient status to normal
                    vioclient_item=aix.models.vioclient.objects.get(id=self.target_instance_number)
                    vioclient_status_normal=aix.models.vioclient_status.objects.get(status_id=5)
                    vioclient_item.status=vioclient_status_normal
                    vioclient_item.save()
                
                elif self.function.name=='ShutdownVIOClient':
                    vioclient_item=aix.models.vioclient.objects.get(id=self.target_instance_number)
                    vioclient_status_poweroff=aix.models.vioclient_status.objects.get(status_id=6)
                    vioclient_item.status=vioclient_status_poweroff
                    vioclient_item.save()
               
        sq=workflow.models.ServiceRequest.objects.get(id=self.service_request_id)
        sq_status_succeed=workflow.models.RequestStatus.objects.get(request_status_id=12)
        sq.request_status=sq_status_succeed
        sq.status_message=workflow_description.ServiceRequestStatusMessage['succeed']
        sq.save()
    
                

    
######################################################################
#                                                                    #
#                                                                    #
#                  Workflow Engine                                   #
#                                                                    #
#                                                                    #
######################################################################
@receiver(pre_save,sender=check_task,dispatch_uid='pre_save_check_task_status_change')
def pre_save_check_task(sender,instance,**kwargs):
    if instance.id:
        old_instance=check_task.objects.get(pk=instance.id)
        task_ready_to_execute=task_status.objects.get(name='ready_to_execute')
        task_executing=task_status.objects.get(name='executing')
        task_created=task_status.objects.get(name='created')
        task_error=task_status.objects.get(name='error')
        task_finished=task_status.objects.get(name='finished')
        task_succeed=task.status.objects.get(name='succeed')
        
        #from created to ready to execute
        if old_instance.status==task_created and instance.status==task_ready_to_execute:
            #run check_task
            run_check_task(instance)

        if (old_instance.status==task_created or old_instance.status==task_ready_to_execute) and instance.status==task_executing:
            #begin to check check_task
            #start a thread to check result
            retry_count=10#one retry sleep 10 second
            t=EThread(GetResponse,(instance,retry_count))
            try:
                t.start()
            except Exception,e:
                logger.error('Error in Checking task: %s' % instance)
                logger.debug(trace_back())
                instance.status=task_error
                #instance.save()
        
        
@receiver(post_save,sender=check_task,dispatch_uid='post_save_check_task_status_change')
def post_save_check_task(sender,instance,**kwargs):
    task_ready_to_execute=task_status.objects.get(name='ready_to_execute')
    task_executing=task_status.objects.get(name='executing')
    task_created=task_status.objects.get(name='created')
    task_error=task_status.objects.get(name='error')
    task_finished=task_status.objects.get(name='finished')
    task_succeed=task.status.objects.get(name='succeed')

    if instance.status==task_finished:
        #check using verdict_condition
        #example: result='5307', verdict_condition="""'%s'=='5307'"""
        #return eval(verdict_condition % result)
        try:
            verdict_str=instance.verdict_condition % instance.result
            check_task_result=eval(verdict_str)
            if check_task_result:
                instance.status=task_succeed
                instance.save()
        except Exception,e:
            logger.error('error in check_task: %s, vererdict: %s, result: %s, error info: %s' % (instance,instance.verdict_condition,instance.result,e))
            logger.debug(trace_back())
            instance.status=task_error
            
    if instance.status==task_error:
        #set task status to error
        task_item=task.objects.get(id=instance.task_id)
        task_item.status=task_error
        task_item.save()

    if instance.status==task_succeed:
        task_item=task.objects.get(id=instance.task_id)
        task_item.status=task_succeed
        task_item.save()
    
@receiver(pre_save,sender=task,dispatch_uid='task_status_change')
def pre_save_task(sender,instance,**kwargs):
    task_ready_to_execute=task_status.objects.get(name='ready_to_execute')
    task_executing=task_status.objects.get(name='executing')
    task_created=task_status.objects.get(name='created')
    task_error=task_status.objects.get(name='error')
    task_finished=task_status.objects.get(name='finished')
    task_succeed=task_status.objects.get(name='succeed')
    if instance.id:
        old_instance=task.objects.get(pk=instance.id)
        logger.debug('EUAO Task status change: %s --> %s' % (old_instance.status,instance.status))
        #from created to executing
        
        if old_instance.status==task_executing and instance.status==task_finished:
            #start check task
            if instance.check_task:
                #set check_task status to ready to execute
                instance.check_task.status=task_ready_to_execute
                instance.check_task.save()
            else:
                instance.status=task_succeed
    
        if old_instance.status==task_created and instance.status==task_executing:
            #check task status_id
            #start a thread to check result
            retry_count=20#one retry sleep 10 second
            if instance.function==euao_service_function.objects.get(name='InstallWholeAIX'):
                retry_count=90
            
            t=EThread(GetResponse,(instance,retry_count))
            try:
                t.start()
            except Exception,e:
                logger.error('Error in Checking task: %s' % instance)
                logger.debug(trace_back())
                instance.status=task_error
                #instance.save()
                
        if (old_instance.status==task_created or old_instance.status==task_executing) and instance.status==task_error:
            logger.debug('euao task from exec to error.')
            if instance.target_type.name=='aix_vioclient':
                if instance.target_instance_number:
                    m_vioclient=aix.models.vioclient.objects.get(id=instance.target_instance_number)
                    vioclient_error_status=aix.models.vioclient_status.objects.get(status_id=8)
                    m_vioclient.status=vioclient_error_status
                    m_vioclient.save()
                    
            try:
                
                sq=workflow.models.ServiceRequest.objects.get(id=instance.service_request_id)
                sq.save()
                sq_status_error_deploy=workflow.models.RequestStatus.objects.get(request_status_id=10)
                sq.request_status=sq_status_error_deploy
                sq.status_message=workflow_description.ServiceRequestStatusMessage['errordeploy']
                sq.save()
            except Exception,e:
                logger.debug(trace_back())
                    
                
@receiver(post_save,sender=task,dispatch_uid='addtask')
def post_save_task(sender,instance,**kwargs):
    
    task_executing=task_status.objects.get(name='executing')
    task_created=task_status.objects.get(name='created')
    task_error=task_status.objects.get(name='error')
    task_finished=task_status.objects.get(name='finished')
    task_succeed=task_status.objects.get(name='succeed')
    
    if instance.status==task_created:
        logger.debug('here we run')
        try:
            s_r_id=instance.service_request_id
            sr=workflow.models.ServiceRequest.objects.get(id=s_r_id)
            #running status
            service_request_running_status=workflow.models.RequestStatus.objects.get(request_status_id=11)
            sr.request_status=service_request_running_status
            logger.debug('euao task run, set service request status to running')
            sr.status_message=workflow_description.ServiceRequestStatusMessage['running']
            sr.save()
            run_task(instance)
        except Exception,e:
            logger.error('Error in running EUAO task: %s' % instance)
            logger.debug(trace_back())
            instance.status=task_error
            instance.save()
    
            
       #set servvice request item to error
    
    if instance.status==task_succeed:
        #set service request status to finished
        instance.set_succeed_result()    
