from django.db import models

from django.db.models.signals import *
from django.dispatch import receiver
from django.contrib.auth.models import User
import datetime

import logging
logger=logging.getLogger('ecms')
import aix.setting as setting
from aix.aix_function import FreezeAIXLockedResource
from aix.aix_function import CreateVIOClient
from aix.aix_function import CreateEUAOTask
from aix.aix_function import delayThreadChangeServiceRequestStatus
import workflow.models
import workflow.description as workflow_description
from ecms.commonfunction import *
import EUAO
import charge

# Create your models here.

    
class resource_available(models.Model):
    available=models.BooleanField(default=True)
    
    def __unicode__(self):
        return 'Available: %s' % self.available
    
class vlan_type(models.Model):
    name=models.CharField(max_length=50)
    description=models.CharField(max_length=50)
    
    def __unicode__(self):
        return self.description

class vlan(models.Model):
    name=models.CharField(max_length=50)
    description=models.CharField(max_length=500,blank=True,null=True)
    vlan_id=models.IntegerField()
    type=models.ForeignKey(vlan_type)
    
    def __unicode__(self):
        return '%s, id: %d, type: %s' % (self.name,self.vlan_id,self.type)
        
    def lock(self):
        status_lock=resource_available.objects.get(available=False)
        self.status=status_lock
        
    def unlock(self):
        status_unlock=resource_available.objects.get(available=True)
        self.status=status_unlock
       
class hdisk_type(models.Model):
    name=models.CharField(max_length=50)
    description=models.CharField(max_length=500,blank=True,null=True)
    
    def __unicode__(self):
        return self.name
    
class vioclient_type(models.Model):
    #depend on the vioclient_type, ccloud should select different vlan ip and hdisks
    name=models.CharField(max_length=50)
    description=models.CharField(max_length=200,blank=True,null=True)
    default_service_vlan=models.ForeignKey(vlan,related_name='service_vlan',blank=True,null=True)
    default_manage_vlan=models.ForeignKey(vlan,related_name='manage_vlan',blank=True,null=True)
    default_hdisk_type=models.ForeignKey(hdisk_type,blank=True,null=True)

    def __unicode__(self):
        return '%s, manage vlan: %s, service vlan: %s, hdisk type: %s' % (self.name,self.default_manage_vlan,self.default_service_vlan,self.default_hdisk_type)

class hmc(models.Model):
    ip=models.IPAddressField()
    username=models.CharField(max_length=50)
    password=models.CharField(max_length=50)
    prompt=models.CharField(max_length=50)
    version=models.CharField(max_length=50,blank=True,null=True)
    
    def __unicode__(self):
        return 'HMC: %s' % self.ip


class nim_server(models.Model):
    ip=models.IPAddressField()
    username=models.CharField(max_length=50)
    password=models.CharField(max_length=50)
    prompt=models.CharField(max_length=50)
    
    def __unicode__(self):
        return 'NIM: %s' % self.ip

class aix_version(models.Model):
    version=models.CharField(max_length=50,unique=True)
    spot=models.CharField(max_length=50)
    lpp_source=models.CharField(max_length=50)
    mksysb=models.CharField(max_length=50)
    
    def __unicode__(self):
        return self.version

class vio_server(models.Model):
    name=models.CharField(max_length=50)
    ip=models.IPAddressField()
    username=models.CharField(max_length=50)
    password=models.CharField(max_length=50)
    prompt=models.CharField(max_length=50)
    def __unicode__(self):
        return '%s: %s' % (self.name,self.ip)

class aix_server(models.Model):
    name=models.CharField(max_length=50)
    alias=models.CharField(max_length=50,blank=True,null=True)
    location=models.CharField(max_length=50,blank=True,null=True)
    hmc_server=models.ForeignKey(hmc)
    total_cpu=models.IntegerField()
    total_mem=models.IntegerField()
    available_cpu=models.IntegerField()
    available_mem=models.IntegerField()
    price=models.IntegerField(blank=True,null=True)
    depreciation_year=models.IntegerField(blank=True,null=True)
    vio_1=models.ForeignKey(vio_server,related_name='aix_server_vioserver_1')
    vio_2=models.ForeignKey(vio_server,related_name='aix_server_vioserver_2')
    
    
    def __unicode__(self):
        return '%s: %s' % (self.alias,self.name)

class vhost(models.Model):
    vhost_name=models.CharField(max_length=50)
    virtual_scsi_adapter=models.CharField(max_length=10)
    aix_server=models.ForeignKey(aix_server)
    status_available=resource_available.objects.get(available=True)
    status=models.ForeignKey(resource_available,default=status_available)
    
    def __unicode__(self):
        return '%s, %s, %s' % (self.vhost_name,self.status,self.aix_server)

    def lock(self):
        status_lock=resource_available.objects.get(available=False)
        self.status=status_lock
    def unlock(self):
        status_unlock=resource_available.objects.get(available=True)
        self.status=status_unlock
        
class hdisk(models.Model):
    rootvg_lun=models.CharField(max_length=100,unique=True)
    aix_server=models.ForeignKey(aix_server)
    vio_1=models.ForeignKey(vio_server,related_name='hdisk_vio_server_1',blank=True,null=True)
    vio_2=models.ForeignKey(vio_server,related_name='hdisk_vio_server_2',blank=True,null=True)
    hdisk_id=models.CharField(max_length=100,blank=True,null=True)
    vio_client_id=models.CharField(max_length=50,blank=True,null=True)
    vhost=models.ForeignKey(vhost,blank=True,null=True)
    vtd_name=models.CharField(max_length=50,blank=True,null=True)
    type=models.ForeignKey(hdisk_type)
    status_available=resource_available.objects.get(available=True)
    status=models.ForeignKey(resource_available,default=status_available)

    def __unicode__(self):
        return 'hdisk: %s,%s' % (self.rootvg_lun,self.status)

    def lock(self):
        status_lock=resource_available.objects.get(available=False)
        self.status=status_lock
    def unlock(self):
        self.vtd_name=None
        self.vhost=None
        self.vio_client_id=None
        status_unlock=resource_available.objects.get(available=True)
        self.status=status_unlock

class aix_ip_status(models.Model):
    status_id=models.IntegerField(unique=True)
    status=models.CharField(max_length=50,unique=True)
    
    def __unicode__(self):
        return "%d, %s" % (self.status_id,self.status)
    
class aix_service_ip(models.Model):
    ip=models.IPAddressField(unique=True)
    netmask=models.IPAddressField(default='255.255.255.0')
    gateway=models.IPAddressField(blank=True,null=True)
    vlan=models.ForeignKey(vlan,blank=True,null=True)
    available_status=aix_ip_status.objects.get(status_id=1)
    status=models.ForeignKey(aix_ip_status,default=available_status)

    def __unicode__(self):
        return '%s, vlan: %s' % (self.ip,self.vlan)
    
    def lock(self):
        locked_status=aix_ip_status.objects.get(status='locked')
        self.status=locked_status
        
    def unlock(self):
        unlocked_status=aix_ip_status.objects.get(status='available')
        self.status=unlocked_status
        
class aix_manage_ip(models.Model):
    ip=models.IPAddressField(unique=True)
    netmask=models.IPAddressField(default='255.255.255.0')
    gateway=models.IPAddressField(blank=True,null=True)
    vlan=models.ForeignKey(vlan,blank=True,null=True)
    available_status=aix_ip_status.objects.get(status_id=1)
    status=models.ForeignKey(aix_ip_status,default=available_status)
    def __unicode__(self):
        return '%s, vlan:%s' % (self.ip,self.vlan)

    def lock(self):
        locked_status=aix_ip_status.objects.get(status='locked')
        self.status=locked_status
    
    def unlock(self):
        unlocked_status=aix_ip_status.objects.get(status='available')
        self.status=unlocked_status


class aix_resource_lock_status(models.Model):
    status=models.CharField(max_length=50)
    
    def __unicode__(self):
        return self.status


class aix_resource_lock(models.Model):
    service_request_id=models.IntegerField()
    aix_server=models.ForeignKey(aix_server,blank=True,null=True)
    cpu=models.IntegerField(blank=True,null=True)
    mem=models.IntegerField(blank=True,null=True)
    aix_service_ip=models.ForeignKey(aix_service_ip,blank=True,null=True)
    aix_manage_ip=models.ForeignKey(aix_manage_ip,blank=True,null=True)
    #hdisk=models.ForeignKey(hdisk,blank=True,null=True)
    # several hdisk, usees rootvg_lun seperated by ','
    hdisk=models.CharField(max_length=200,blank=True,null=True)
    vhost=models.ForeignKey(vhost,blank=True,null=True)
    status=models.ForeignKey(aix_resource_lock_status)
    
    def __unicode__(self):
        return 'Service request id: %d, %s' % (self.service_request_id,self.status.status)

    def FreezeResource(self,ChangeStatus=False):
        logger.info('freeze aix resource')
        try:
            flag=FreezeAIXLockedResource(aix_server=self.aix_server,
                                      cpu=self.cpu,
                                      mem=self.mem,
                                      service_ip=self.aix_service_ip,
                                      manage_ip=self.aix_manage_ip,
                                      hdisks=self.hdisk,
                                      vhost=self.vhost)
           
            return flag
        except Exception,e:
            logger.error('Error in Freezing resource. %s' % e)
            logger.debug('%s' % trace_back())
            return False
        
class vioclient_status(models.Model):
    status_id=models.IntegerField()
    status=models.CharField(max_length=50,unique=True)
    """
    deploying, power on, power off, locked
    """
    
    def __unicode__(self):
        return "status_id: %d, %s" % (self.status_id,self.status)

class vioclient(models.Model):
    belong_to_username=models.CharField(max_length=50)
    latest_service_request_id=models.IntegerField()
    resource_lock_item=models.ForeignKey(aix_resource_lock)
    name=models.CharField(max_length=50,unique=True)
    server=models.ForeignKey(aix_server)
    vioserver_1=models.ForeignKey(vio_server,related_name='vioserver_1')
    vioserver_2=models.ForeignKey(vio_server,related_name='vioserver_2')
    #several hdisk, seperated by ','
    hdisk=models.CharField(max_length=200)
    vhost=models.ForeignKey(vhost)

    service_netcard=models.CharField(max_length=10,default=setting.vioclient_netcard.get('service_netcard'))
    manage_netcard=models.CharField(max_length=10,default=setting.vioclient_netcard.get('manage_netcard'))
    service_ip=models.ForeignKey(aix_service_ip,unique=True)
    manage_ip=models.ForeignKey(aix_manage_ip,unique=True)
    
    username=models.CharField(max_length=50,default=setting.vioclient_default_user)
    password=models.CharField(max_length=50,default=setting.vioclient_default_passwd)
    
    nim_server=models.ForeignKey(nim_server)
    os_version=models.ForeignKey(aix_version)
    
    min_procs=models.IntegerField(default=setting.min_procs)
    desired_procs=models.IntegerField()
    max_procs=models.IntegerField(default=setting.max_procs)
    
    min_procs_unit=models.FloatField(default=setting.min_procs_unit)
    desired_procs_unit=models.FloatField()
    max_procs_unit=models.FloatField(default=setting.max_procs_unit)
    
    min_mem=models.IntegerField(default=setting.min_mem)
    desired_mem=models.IntegerField()
    max_mem=models.IntegerField(default=setting.max_mem)
    
    virtual_eth_adapters=models.CharField(max_length=200)
    #virtual_scsi_adapter=models.CharField(max_length=50,default=setting.vioclient_virtual_scsi_adapter)
    
    status=models.ForeignKey(vioclient_status)
    
    def __unicode__(self):
        return 'User: %s, Name:%s, ManageIP:%s, ServiceIP: %s, Status:%s' % (self.belong_to_username,self.name,self.manage_ip.ip,self.service_ip.ip,self.status.status)

    

    
######################################################################
#                                                                    #
#                                                                    #
#                  Workflow Engine                                   #
#                                                                    #
#                                                                    #
######################################################################

@receiver(pre_save,sender=vioclient,dispatch_uid='pre_save_vioclient')
def pre_save_vioclient(sender,instance,**kwargs):
    
    
    vm_status_deploying=vioclient_status.objects.get(status_id=1)
    vm_status_ready_to_deploy=vioclient_status.objects.get(status_id=0)
    vm_status_error_deploy=vioclient_status.objects.get(status_id=8)
    vm_status_normal=vioclient_status.objects.get(status_id=5)
    vm_status_power_off=vioclient_status.objects.get(status_id=6)
    vm_status_deleting=vioclient_status.objects.get(status_id=3)
            
    if instance.id:
        old_vioclient_instance=vioclient.objects.get(pk=instance.id)
        if old_vioclient_instance.status==vm_status_power_off and instance.status==vm_status_deleting:
            #begin to delete the vioclient
            #mark vioclient usage log
            try:
                vul=charge.models.vioclient_usage_log.objects.filter(vioclient_name=instance.name).order_by('-id')[0]
                vul.end_date=datetime.date.today()
                vul.use_days=(vul.end_date-vul.start_date).days
                vul.save()
                
            except Exception,e:
                logger.error('Can not find vioclient log for: %s.' % instance.name)
                logger.debug(trace_back())
        
        if old_vioclient_instance.status==vm_status_deploying and instance.status==vm_status_normal:
            # change from deploying to normal
            # add vioclient usage log.
            logger.info('vioclient %s is ready from %s.' % (instance.name,datetime.date.today()))
            vul=charge.models.vioclient_usage_log()
            vul.vioclient_user=instance.belong_to_username
            vul.vioclient_name=instance.name
            vul.vioclient_cpu=instance.desired_procs
            vul.vioclient_mem=instance.desired_mem
            vul.use_days=0
            vul.start_date=datetime.date.today()
            vul.save()
            logger.debug('vioclient usage log is added. vioclient name: %s' % instance.name)
        
        if old_vioclient_instance.status==vm_status_ready_to_deploy and instance.status==vm_status_deploying:
            try:
                sq_id=instance.latest_service_request_id
                sq=workflow.models.ServiceRequest.objects.get(id=sq_id)
                sq.save()
                sq_status_running=workflow.models.RequestStatus.objects.get(request_status_id=11)
                sq.request_status=sq_status_running
                sq.status_message=workflow_description.ServiceRequestStatusMessage['running']
                sq.save()
            except Exception,e:
                logger.debug(trace_back())
            
        if old_vioclient_instance.status==vm_status_ready_to_deploy and instance.status==vm_status_error_deploy:
            try:
                sq_id=instance.latest_service_request_id
                
                sq_status_error_deploy=workflow.models.RequestStatus.objects.get(request_status_id=10)
                delayThreadChangeServiceRequestStatus(sq_id,sq_status_error_deploy)
                """
                sq=workflow.models.ServiceRequest.objects.get(id=sq_id)
                sq.save()
                sq_status_error_deploy=workflow.models.RequestStatus.objects.get(request_status_id=10)
                sq.request_status=sq_status_error_deploy
                sq.status_message=workflow_description.ServiceRequestStatusMessage['errordeploy']
                sq.save()
                """
            except Exception,e:
                logger.debug(trace_back())
    
    else:
        #no instance.id, newly created
        pass
       
    
@receiver(post_save,sender=vioclient,dispatch_uid='post_save_vioclient')
def post_save_vioclient(sender,instance,**kwargs):
    vm_status_ready_to_deploy=vioclient_status.objects.get(status_id=0)
    vm_status_deploying=vioclient_status.objects.get(status_id=1)
    """
    vm_status_ready_to_deploy=vioclient_status.objects.get(status_id=0)
    """
    vm_status_error_deploy=vioclient_status.objects.get(status_id=8)
    if instance.status==vm_status_deploying:
        #set euao task target_instance_number
        sr_id=instance.latest_service_request_id
        m_euao_task=EUAO.models.task.objects.get(service_request_id=sr_id)
        m_euao_task.target_instance_number=instance.id
        m_euao_task.save()
        logger.info('save target_instance_number')
        
            
        
    if instance.status==vm_status_ready_to_deploy:
    #send to EUAO to provision
        try:
            CreateEUAOTask(instance)
            instance.status=vm_status_deploying
            instance.save()
        except Exception,e:
            logger.error('Error in Create euao task. %s' % e)
            logger.debug(trace_back())
            instance.status=vm_status_error_deploy
            instance.save()


@receiver(pre_save,sender=aix_resource_lock,dispatch_uid='aixlockresource')
def pre_save_aix_resource_locked(sender,**kwargs):
    #before lock item has been added, status chan
    instance=kwargs.get('instance')
    if instance.id:
        old_aix_resource_lock=aix_resource_lock.objects.get(pk=instance.id)
        
        if old_aix_resource_lock.status.status=='request' and instance.status.status=='freezed':
            logger.debug('request to freezed')
            logger.debug('pre_status: request, post_status: freeze')
            if not instance.FreezeResource():
                instance.state='Freeze Error'
                instance.status=aix_resource_lock_status.objects.get(status='Error')
            else:
                instance.status=aix_resource_lock_status.objects.get(status='freezed')
                
                service_request_id=instance.service_request_id
                service_request=workflow.models.ServiceRequest.objects.get(id=service_request_id)
                request_parameter=service_request.request_parameter
                try:
                    #translate str to dict type
                    request_parameter=eval(request_parameter)
                except Exception,e:
                    logger.error('Request parameter %s is not a dict form string. %s',(request_parameter,e))
                    return
                resource_type=request_parameter.get('type')
                if resource_type=='aix':
                    #create a vmware_machine item, status is deploying
                    try:
                        CreateVIOClient(instance,service_request)
                        """
                        #set ServiceRequest Status to 'plan to implement'
                        #service_request.request_status=workflow.models.RequestStatus.objects.get(request_status_id=3)
                        #service_request.save()
                        """
                        
                    except Exception,e:
                        logger.debug(trace_back())
                        logger.error('Error in Create aix vioclient. %s' % e)
                else:
                    logger.error('resource_type: %s not supported.' % resource_type)                    

        if old_aix_resource_lock.status.status=='freezed' and instance.status.status=='free':
            #set the resources in this item to available, add the cpu, mem to aix_server
            
            if instance.aix_server:
                instance.aix_server.available_cpu+=instance.cpu
                instance.aix_server.available_mem+=instance.mem
            
            hdisk_item_list=[]                
            if instance.hdisk:
                hdisks_list=instance.hdisk.split(',')
                for hdisk_item_str in hdisks_list:
                    hdisk_item=hdisk.objects.get(rootvg_lun=hdisk_item_str)
                    hdisk_item_list.append(hdisk_item)
                    hdisk_item.unlock()
            if instance.vhost:
                instance.vhost.unlock()
            
            if instance.aix_manage_ip:
                instance.aix_manage_ip.unlock()
            if instance.aix_service_ip:
                instance.aix_service_ip.unlock()
            
            if instance.aix_server:
                instance.aix_server.save()
            if len(hdisk_item_list)>0:
                for item in hdisk_item_list:
                    item.save()
            if instance.vhost:
                instance.vhost.save()
            
            if instance.aix_service_ip:
                instance.aix_service_ip.save()
            if instance.aix_manage_ip:
                instance.aix_manage_ip.save()

###################################################################### #                                                                    # #                                                                    #
#                  Server config helper                              #
#                                                                    #
#                                                                    #
######################################################################

#when add a hdisk, automatically find vio_1, vio_2 after aix_server selected
@receiver(pre_save,sender=hdisk,dispatch_uid='add_hdisk_to_server')
def pre_save_hdisk(sender,instance,**kwargs):
    if not instance.id:
        #new added
        if instance.aix_server:
            instance.vio_1=instance.aix_server.vio_1
            instance.vio_2=instance.aix_server.vio_2
    
