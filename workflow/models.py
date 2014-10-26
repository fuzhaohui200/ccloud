# -*- coding: utf-8 -*-
import datetime
from django.db import models

from django_fsm.db.fields import FSMField
from django_fsm.db.fields import transition
import logging
logger=logging.getLogger('ecms')

from django.db.models.signals import *
from django.dispatch import receiver

from django.contrib.auth.models import User
from ecms.EThread import EThread
from vmware.models import vmware_datastore
from vmware.models import vmware_server

from ecms.commonfunction import *
from workflow.workflow_function import CheckResourcePoolAvailable
from workflow.workflow_function import CheckUserQuotaAvailable
from workflow.workflow_function import CheckResourceBelongToUser
from workflow.workflow_function import check_vm_name
from workflow.workflow_function import check_aix_name
from workflow.workflow_function import ChangeUserQuotaUsage
from workflow.workflow_function import passApprove
from workflow.workflow_function import CreateEUAOTaskFromServiceRequest
from workflow.workflow_function import setServiceRequestApprover
from workflow.workflow_function import check_if_sysadmin
from workflow.workflow_function import setServiceRequestStatus
from workflow.description import *
import workflow.setting as setting

import EUAO.models
# Create your models here.
#UserProfile,RequestStatus,RequestType,ServiceRequest,ApproveStatus,Approve

#user addtional profile
class UserProfile(models.Model):
    user=models.OneToOneField(User)
    company=models.CharField(max_length=50,blank=True,default='CES')
    branch_bank=models.CharField(max_length=50,blank=True,default='总行')
    department=models.CharField(max_length=50,blank=True,default='开发部')
    project_group=models.CharField(max_length=50,blank=True)
    #vmware quota
    vmware_cpu_quota=models.IntegerField(blank=True,default=setting.vmware_cpu_quota)
    vmware_mem_quota=models.IntegerField(blank=True,default=setting.vmware_mem_quota)
    vmware_machine_count_quota=models.IntegerField(blank=True,default=setting.vmware_machine_count_quota)
    
    vmware_cpu_used=models.IntegerField(blank=True,default=0)
    vmware_mem_used=models.IntegerField(blank=True,default=0)
    vmware_machine_count_used=models.IntegerField(blank=True,default=0)
    
    aix_cpu_quota=models.IntegerField(blank=True,default=setting.aix_cpu_quota)
    aix_mem_quota=models.IntegerField(blank=True,default=setting.aix_mem_quota)
    aix_count_quota=models.IntegerField(blank=True,default=setting.aix_vioclient_count_quota)
    
    aix_cpu_used=models.IntegerField(blank=True,default=0)
    aix_mem_used=models.IntegerField(blank=True,default=0)
    aix_count_used=models.IntegerField(blank=True,default=0)
       
       
    
    def save(self, *args, **kwargs):
        if not self.pk:
            try:
                p = UserProfile.objects.get(user=self.user)
                self.pk = p.pk
            except UserProfile.DoesNotExist:
                pass
        super(UserProfile, self).save(*args, **kwargs)
        
#Request Status:
# 0:submitted   1: under approval  2:fail approval 3:plan to implement  4:fail implimentation 5: succeed 6:not enough resource
class RequestStatus(models.Model):
    request_status_id=models.IntegerField()
    request_status_caption=models.CharField(max_length=100)
    
    def __unicode__(self):
        return "status id: %d, %s" %(self.request_status_id,self.request_status_caption)

#Request Type:
class RequestType(models.Model):
    request_type_id=models.IntegerField()
    request_type_caption=models.CharField(max_length=100)
    
    def __unicode__(self):
        return "request type id: %d, %s" % (self.request_type_id,self.request_type_caption)



#service request table
class ServiceRequest(models.Model):
    state=FSMField(default='submitted',blank=True,null=True)
    user=models.ForeignKey(User)
    submitter=models.CharField(max_length=50)
    description=models.TextField()
    request_type=models.ForeignKey(RequestType)
    request_parameter=models.CharField(max_length=1000)
    submit_time=models.DateTimeField(editable=False,blank=True,null=True)
    last_modify_time=models.DateTimeField(blank=True,null=True)
    request_status=models.ForeignKey(RequestStatus,)
    status_message=models.CharField(max_length=500,blank=True,null=True)
    approver=models.CharField(max_length=50,blank=True,null=True)
    
    def __unicode__(self):
        return "ID: %d,Submitter: %s, description: %s." % (self.id,self.submitter,self.description)
    
    def save(self,*args,**kwargs):
        if not self.id:
            self.submit_time=datetime.datetime.today()
            request_status=RequestStatus.objects.get(request_status_id=0)
            self.submitter=self.user.username
        self.last_modify_time=datetime.datetime.today()
        return super(ServiceRequest,self).save(*args,**kwargs)
        
#Approval Status: 0: under approval  1:pass  2:fail
class ApproveStatus(models.Model):
    approve_status_id=models.IntegerField()
    approve_status_caption=models.CharField(max_length=100)
    
    def __unicode__(self):
        return "id: %d, caption: %s" % (self.approve_status_id,self.approve_status_caption)

#Approval Table
class Approve(models.Model):
    service_request_id=models.IntegerField()
    submitter=models.CharField(max_length=50)
    submit_time=models.DateTimeField(editable=False)
    last_modify_time=models.DateTimeField(blank=True,null=True)
    approve_status=models.ForeignKey(ApproveStatus)
    request_description=models.CharField(max_length=500)
    approver=models.CharField(max_length=50,blank=True,null=True)
    
    def __unicode__(self):
        #return "id: %d, status: %s,description: %s" % (self.service_request_id,self.approve_status,self.request_description)
    
        return "service request id: %d, status:%s, description: %s" % (self.service_request_id,self.approve_status.approve_status_caption,self.request_description)
    
    def save(self,*args,**kwargs):
        ''' On save, update timestamps '''
        if not self.id:
            self.submit_time= datetime.datetime.today()
        self.last_modify_time = datetime.datetime.today()
        super(Approve, self).save(*args, **kwargs)

class SystemResourceAlertStatus(models.Model):
    status_id=models.IntegerField()
    status=models.CharField(max_length=50)
    
    def __unicode__(self):
        return 'Statusid: %d, Status: %s' % (self.status_id,self.status)

class SystemResourceAlert(models.Model):
    service_request_id=models.IntegerField()
    username=models.CharField(max_length=50)
    submit_time=models.DateTimeField(editable=False)
    last_modify_time=models.DateTimeField(blank=True,null=True)
    request_description=models.CharField(max_length=500)
    status=models.ForeignKey(SystemResourceAlertStatus)
    
    def __unicode__(self):
        return 'service_request_id: %d, status: %s' % (self.service_request_id,self.status.status)
    
    def save(self,*args,**kwargs):
        ''' On save, update timestamps '''
        if not self.id:
            self.submit_time= datetime.datetime.today()
        self.last_modify_time = datetime.datetime.today()
        super(SystemResourceAlert, self).save(*args, **kwargs)
        

#addtional user info
def create_user_profile(sender,instance,created,**kwargs):
    if created:
        #UserProfile.objects.create(user=instance)
        UserProfile.objects.get_or_create(user=instance)

post_save.connect(create_user_profile,sender=User)
    
    
######################################################################
#                                                                    #
#                                                                    #
#                  Workflow Engine                                   #
#                                                                    #
#                                                                    #
######################################################################
    
# model operation signal
@receiver(pre_save,sender=ServiceRequest)
def ServiceRequest_pre_save(sender,instance,**kwargs):
    #request_status_id:0, submitted
    request_submited=RequestStatus.objects.get(request_status_id=0)
    request_sendtoapproval=RequestStatus.objects.get(request_status_id=1)
    request_underapproval=RequestStatus.objects.get(request_status_id=2)
    request_failapproval=RequestStatus.objects.get(request_status_id=3)
    request_passapproval=RequestStatus.objects.get(request_status_id=4)
    request_planimplement=RequestStatus.objects.get(request_status_id=5)
    request_resource_not_available=RequestStatus.objects.get(request_status_id=6)
    request_resource_fixed=RequestStatus.objects.get(request_status_id=9)
    request_error_deploy=RequestStatus.objects.get(request_status_id=10)
    request_running=RequestStatus.objects.get(request_status_id=11)
    request_error=RequestStatus.objects.get(request_status_id=13)
    request_revoked=RequestStatus.objects.get(request_status_id=14)
    
    request_parameter=instance.request_parameter
        #convert request_parameter from string to dict
    try:
        request_parameter=eval(request_parameter)
    except Exception,e:
        logger.error('Request parameter %s is not a dict form string. %s',(request_parameter,e))
        instance.request_status=request_error
        return
    
    if instance.id:
        old_instance=ServiceRequest.objects.get(pk=instance.id)
        
        logger.debug('Service request status change: %s --> %s' % (old_instance.request_status,instance.request_status))
        allow_revoke_request_status_id_list=[2,6,13]
        
        
        #revoke
        if (old_instance.request_status.request_status_id in allow_revoke_request_status_id_list) and instance.request_status.request_status_id==14:
            #revoke
            if old_instance.request_status==request_underapproval:
                #delete the approve item
                approve_item=Approve.objects.get(service_request_id=old_instance.id)
                approve_item.delete()
                logger.debug('Approve item: %s is deleted for service request is revoked.' % approve_item)
            
            if old_instance.request_status==request_resource_not_available:
                #check if there is an approve item.
                approve_item_list=Approve.objects.filter(service_request_id=old_instance.id)
                if len(approve_item_list)>0:
                    approve_item_list[0].delete()
                    logger.debug('Approve item: %s is deleted for service request is revoked.' % approve_item_list[0])
                
                #set system resource alert status to '请求已撤销'
                system_resource_alert_item=SystemResourceAlert.objects.get(service_request_id=old_instance.id)
                system_resource_alert_status_revoked=SystemResourceAlertStatus.objects.get(status_id=2)
                system_resource_alert_item.status=system_resource_alert_status_revoked
                system_resource_alert_item.save()
                
                    
            #revoke this service request, reset the user quota info
            logger.debug('Revoke service request: %s', old_instance)
            
            try:
                request_parameter=eval(instance.request_parameter)
                
                ChangeUserQuotaUsage(instance.submitter,instance.request_type,request_parameter,revoke=True)            
            except Exception,e:
                logger.error('Request parameter %s is not a dict form string. %s',(request_parameter,e))
                logger.debug(trace_back())
                return
        
        #fail approval
        if old_instance.request_status==request_underapproval and instance.request_status==request_failapproval:
            #reset user quota info
            
            logger.debug('Deny service request: %s', old_instance)
            
            try:
                request_parameter=eval(instance.request_parameter)
                
                ChangeUserQuotaUsage(instance.submitter,instance.request_type,request_parameter,revoke=True)            
            except Exception,e:
                logger.error('Request parameter %s is not a dict form string. %s',(request_parameter,e))
                logger.debug(trace_back())
                return
                
        if old_instance.request_status==request_submited and instance.request_status==request_planimplement:
            #for recycling resource
            m_request_type=instance.request_type
            if m_request_type.request_type_id==3 or m_request_type.request_type_id==2:
                #recycling resource request
                CreateEUAOTaskFromServiceRequest(instance)
                instance.request_status=request_running
                instance.status_message=ServiceRequestStatusMessage['running']
        #pass approval
        
            
        if old_instance.request_status==request_underapproval and instance.request_status.request_status_id==4:
            #pass approval
            #pass approval, pass user quota chck,
            #check resource available
            
            
            logger.debug('service request: underapproval to pass')
            logger.debug('check resource available')
            if CheckResourcePoolAvailable(service_request_id=instance.id,request_parameter=request_parameter):
                logger.debug('Pass approval, Service Request %d is implementing' % instance.id)
                instance.request_status=request_running
                instance.status_message=ServiceRequestStatusMessage['running']
            else:
                #ResourcePoolNotAvailable, but within UserQuota
                #send a message to Sysadmin, and tell user sysadmin is working.
                logger.error('System resource not available, but the request is within user quota.')
                #set to request_resource_not_available
                t=EThread(setServiceRequestStatus,(instance,request_resource_not_available,ServiceRequestStatusMessage['resourcenotavailable']))
                t.start()
                """
                instance.request_status=request_resource_not_available
                instance.status_message=ServiceRequestStatusMessage['resourcenotavailable']
                """
                
        #need approval, send to approval
            
        if old_instance.request_status==request_submited and instance.request_status==request_sendtoapproval:
            #Add approval item
            ap=Approve(service_request_id=instance.id,
                       submitter=instance.submitter,
                       approve_status=ApproveStatus.objects.get(approve_status_id=0),
                       request_description='Submitter: %s, Request info: %s' % (instance.submitter,instance.request_parameter))
            ap.save()
            instance.request_status=request_underapproval
        
            
        if old_instance.request_status!=request_resource_not_available and instance.request_status==request_resource_not_available:
            # alert the sysadmin
            logger.debug('old request_status: %s' % old_instance.request_status)
            logger.debug('new reqeust_status: %s' % instance.request_status)
            systemalert_resourcenotavailable=SystemResourceAlertStatus.objects.get(status_id=0)
            systemalert_resourcenfixed=SystemResourceAlertStatus.objects.get(status_id=1)
            
            systemalert=SystemResourceAlert()
            systemalert.service_request_id=instance.id
            systemalert.username=instance.submitter
            systemalert.request_description=instance.request_parameter
            systemalert.status=systemalert_resourcenotavailable
            systemalert.save()
            logger.debug('new system resource alert added')
            
        if old_instance.request_status==request_resource_not_available and instance.request_status==request_resource_fixed:
            logger.debug('Service Request status change from resource_not_available to _fixed')
            if CheckResourcePoolAvailable(service_request_id=instance.id,request_parameter=request_parameter):
                logger.debug('Resource problem fixed. Service Request %d is implementing' % instance.id)
                instance.request_status=request_planimplement
                instance.status_message=ServiceRequestStatusMessage['planimplement']
                #instance.save()
            else:
                #ResourcePoolNotAvailable, but within UserQuota
                #send a message to Sysadmin, and tell user sysadmin is working.
                logger.error('System resource not available, but the request is within user quota.')
                instance.request_status=request_resource_not_available
                instance.status_message=ServiceRequestStatusMessage['resourcenotavailable']
        
        if old_instance.request_status==request_planimplement and instance.request_status==request_error_deploy:
            #E-mail Alert sysadmin
            instance.status_message=ServiceRequestStatusMessage['errordeploy']
            pass
        
    else:
        pass    
                            

@receiver(post_save,sender=ServiceRequest)
def ServiceRequest_post_save(sender,instance,**kwargs):
    request_submited=RequestStatus.objects.get(request_status_id=0)
    request_sendtoapproval=RequestStatus.objects.get(request_status_id=1)
    request_underapproval=RequestStatus.objects.get(request_status_id=2)
    request_failapproval=RequestStatus.objects.get(request_status_id=3)
    request_passapproval=RequestStatus.objects.get(request_status_id=4)
    request_planimplement=RequestStatus.objects.get(request_status_id=5)
    request_resource_not_available=RequestStatus.objects.get(request_status_id=6)
    request_resource_conflict=RequestStatus.objects.get(request_status_id=8)
    request_error=RequestStatus.objects.get(request_status_id=13)
    request_parameter=instance.request_parameter
        #convert request_parameter from string to dict
    try:
        request_parameter=eval(request_parameter)
    except Exception,e:
        logger.error('Request parameter %s is not a dict form string. %s',(request_parameter,e))
        return
    if instance.request_status.request_status_id==0:
        #submitted
        logger.debug('new service request submitted.')
            
        #check user quota
        """
        request_type_applyresource=RequestType.objects.get(request_type_id=1)
        request_type_adjustresource=RequestType.objects.get(request_type_id=2)
        request_type_recycleresource=RequestType.objects.get(request_type_id=3)
        """
        m_request_type=instance.request_type
        
        if m_request_type.request_type_id==1:
            if request_parameter.get('type')=='vmware_machine':
                if check_vm_name(request_parameter.get('name')):
                    instance.request_status=request_resource_conflict
                    instance.status_message=ServiceRequestStatusMessage['resourceconflict']
                    instance.save()
                    return
            
            if request_parameter.get('type')=='aix':
                logger.debug('New aix request. service reqeust id: %d' % instance.id)
                if check_aix_name(request_parameter.get('name')):
                    instance.request_status=request_resource_conflict
                    instance.status_message=ServiceRequestStatusMessage['resourceconflict']
                    instance.save()
                    return
            
            if CheckUserQuotaAvailable(instance.submitter,m_request_type,request_parameter):
                #within user quota
                
                #check resource pool
                if CheckResourcePoolAvailable(service_request_id=instance.id,request_parameter=request_parameter):
                    logger.debug('Service Request %d is implementing' % instance.id)
                    
                    instance.request_status=request_planimplement
                    #instance.status_message=ServiceRequestStatusMessage['planimplement']
                    instance.status_message=ServiceRequestStatusMessage['running']
                    instance.save()
                else:
                    #ResourcePoolNotAvailable, but within UserQuota
                    #send a message to Sysadmin, and tell user sysadmin is working.
                    logger.error('System resource not available, but the request is within user quota.')
                    instance.request_status=request_resource_not_available
                    instance.status_message=ServiceRequestStatusMessage['resourcenotavailable']
                    instance.save()
            else:
                #request over quota
                ChangeUserQuotaUsage(username=instance.submitter,request_type=m_request_type,request_parameter=request_parameter)
                logger.debug("Service Request: %d over %s quota. Need approval." % (instance.id,instance.submitter))
                instance.request_status=request_sendtoapproval
                instance.status_message=ServiceRequestStatusMessage['underapproval']
                instance.save()
        
        elif m_request_type.request_type_id==3:
            #recycle the resource
            #no need to check quota
            #check the resource is belong to user
            if CheckResourceBelongToUser(instance.submitter,request_parameter) or check_if_sysadmin(instance.submitter):
                #add euao task,
                instance.request_status=request_planimplement
                instance.status_message=ServiceRequestStatusMessage['planimplement']
                instance.save()
        
        elif m_request_type.request_type_id==2:
            #modify the resource
            #eg: poweroff,poweron,reset to vioclient
            if CheckResourceBelongToUser(instance.submitter,request_parameter) or check_if_sysadmin(instance.submitter):
                #add euao task
                instance.request_status=request_planimplement
                instance.status_message=ServiceRequestStatusMessage['planimplement']
                instance.save()
    
    
        
    
@receiver(pre_save,sender=Approve)
def pre_save_Approve(sender,instance,**kwargs):
    #approve_status
    approve_underapproval=ApproveStatus.objects.get(approve_status_id=0)
    approve_pass=ApproveStatus.objects.get(approve_status_id=1)
    approve_fail=ApproveStatus.objects.get(approve_status_id=2)
    approve_pending=ApproveStatus.objects.get(approve_status_id=3)
    
    if instance.id:
        old_instance=Approve.objects.get(pk=instance.id)
        
        logger.debug('Approve status change: %s --> %s' % (old_instance.approve_status, instance.approve_status))
        if (old_instance.approve_status==approve_underapproval or old_instance.approve_status==approve_pending) and instance.approve_status==approve_pass:
            logger.debug('Request status change to PASS.')
            #passApprove(instance)
            t=EThread(passApprove,(instance,))
            t.start() 
        """
            #pass the service request
            #change to thread
            
            sr=ServiceRequest.objects.get(id=instance.service_request_id)
            request_passapproval=RequestStatus.objects.get(request_status_id=4)
            sr.request_status=request_passapproval
            sr.save()
        """
        if (old_instance.approve_status==approve_underapproval or old_instance.approve_status==approve_pending) and instance.approve_status==approve_fail:
            #fail the approve
            try:
                sr=ServiceRequest.objects.get(id=instance.service_request_id)
                request_failapproval=RequestStatus.objects.get(request_status_id=3)
                sr.request_status=request_failapproval
                sr.status_message=ServiceRequestStatusMessage['failapproval']
                sr.save()
                t=EThread(setServiceRequestApprover,(instance.id,))
                t.start()
            except Exception,e:
                logger.debug(trace_back())

@receiver(post_save,sender=Approve)
def post_save_Approve(sender,instance,**kwargs):
    approve_pass=ApproveStatus.objects.get(approve_status_id=1)
    if instance.approver:
        sr=ServiceRequest.objects.get(id=instance.service_request_id)
        if sr.approver!=instance.approver:
            sr.approver=instance.approver
            sr.save()

@receiver(pre_save,sender=SystemResourceAlert)
def pre_save_SystemResourceAlert(sender,instance,**kwargs):
    system_resource_not_enough=SystemResourceAlertStatus.objects.get(status_id=0)
    system_resource_fixed=SystemResourceAlertStatus.objects.get(status_id=1)
    if instance.id:
        old_instance=SystemResourceAlert.objects.get(pk=instance.id)
        if old_instance.status==system_resource_not_enough and instance.status==system_resource_fixed:
            logger.debug('SystemResourceAlert change to resource_fixed')
            try:
                sr=ServiceRequest.objects.get(id=instance.service_request_id)
                sr_status_resource_fixed=RequestStatus.objects.get(request_status_id=9)
                sr.request_status=sr_status_resource_fixed
                sr.status_message=ServiceRequestStatusMessage['resourcefixed']
                logger.debug('service request %d fixed.' % instance.service_request_id)
                sr.save()
            except Exception,e:
                logger.error(trace_back())
