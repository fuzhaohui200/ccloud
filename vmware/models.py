from django.db import models

from django.db.models.signals import *
from django.dispatch import receiver

from django_fsm.db.fields import FSMField
from django_fsm.db.fields import transition

import logging
logger=logging.getLogger('ecms')

from vmware.vmware_function import CreateEUAOTask
from vmware.vmware_function import CreateVMware_machine
from vmware.vmware_function import FreezeVMwareLockedResource

import workflow.models
# Create your models here.
class vmware_os_type(models.Model):
    os_type=models.CharField(max_length=50)
    os_version=models.CharField(max_length=100)
    os_concat=models.CharField(max_length=150,blank=True)

    def save(self,*args,**kwargs):
        self.os_concat=self.os_type+'-'+self.os_version
        return super(vmware_os_type,self).save(*args,**kwargs)
    
    def __unicode__(self):
        return '%s, %s' % (self.os_type,self.os_version)

class vmware_template(models.Model):
    name=models.CharField(max_length=50,unique=True)
    path=models.CharField(max_length=200,unique=True)
    cpu=models.IntegerField()
    mem=models.IntegerField()
    disk_space=models.IntegerField()
    os_type=models.ForeignKey(vmware_os_type)
    username=models.CharField(max_length=50)
    password=models.CharField(max_length=50)
    licence_key=models.CharField(max_length=200,blank=True,null=True)
    
    def __unicode__(self):
        return '%s' % self.name

class vmware_vcenter(models.Model):
    ip=models.IPAddressField(unique=True)
    webservice_url=models.CharField(max_length=200,unique=True)
    username=models.CharField(max_length=50)
    password=models.CharField(max_length=50)

    def __unicode__(self):
        return 'VCenter: %s' % self.ip
    
# vmware server
class vmware_server(models.Model):
    name=models.CharField(max_length=30,unique=True)
    location=models.CharField(max_length=50)
    vcenter=models.ForeignKey(vmware_vcenter)
    ip=models.IPAddressField(unique=True)
    username=models.CharField(max_length=30)
    password=models.CharField(max_length=30)
    
    total_storage_capacity_gb=models.IntegerField()
    available_storage_capacity_gb=models.IntegerField()
    total_cpu=models.IntegerField()
    available_cpu=models.IntegerField()
    total_mem_gb=models.IntegerField()
    available_mem_gb=models.IntegerField()
    
    price=models.IntegerField()
    depreciation_year=models.IntegerField()
    
    def __unicode__(self):
        return 'EXS: %s, %s' % (self.name,self.ip)
    

class vmware_datastore_type(models.Model):
    type=models.CharField(max_length=50,unique=True)
    
    def __unicode__(self):
        return '%s' % self.type
    
class vmware_datastore(models.Model):
    name=models.CharField(max_length=50,unique=True)
    total_capacity_gb=models.IntegerField()
    available_capacity_gb=models.IntegerField()
    datastore_type=models.ForeignKey(vmware_datastore_type)
    esx=models.ForeignKey(vmware_server,blank=True,null=True)
    price=models.IntegerField()
    depreciation_year=models.IntegerField()
    
    def __unicode__(self):
        return 'Datastore: %s' % self.name


class vmware_datacenter(models.Model):
    name=models.CharField(max_length=50,unique=True)
    
    def __unicode__(self):
        return '%s' % self.name

class vmware_machine_status(models.Model):
    status_id=models.IntegerField(unique=True)
    status=models.CharField(max_length=30,unique=True)
    
    def __unicode__(self):
        return '%d,%s' % (self.status_id,self.status)

class vmware_ip_status(models.Model):
    status_id=models.IntegerField(unique=True)
    status=models.CharField(max_length=50,unique=True)
    
    def __unicode__(self):
        return "%d, %s" % (self.status_id,self.status)

class vmware_manage_ip(models.Model):
    ip=models.IPAddressField(unique=True)
    netmask=models.IPAddressField(default='255.255.255.0')
    gateway=models.IPAddressField(blank=True,null=True)
    available_status=vmware_ip_status.objects.get(status_id=0)
    status=models.ForeignKey(vmware_ip_status,default=available_status)
    
    def __unicode__(self):
        return "%s, %s" % (self.ip,self.status.status)

    def save(self,*args,**kwargs):
        return super(vmware_manage_ip,self).save(*args,**kwargs)
    
    def lock(self):
        self.status=vmware_ip_status.objects.get(status='locked')
        #self.save()
    
    def unlock(self):
        self.status=vmware_ip_status.objects.get(status='available')
    
class vmware_service_ip(models.Model):
    ip=models.IPAddressField(unique=True)
    netmask=models.IPAddressField(default='255.255.255.0')
    gateway=models.IPAddressField(blank=True,null=True)
    available_status=vmware_ip_status.objects.get(status_id=0)
    status=models.ForeignKey(vmware_ip_status,default=available_status)
    
    def __unicode__(self):
        return "%s, %s" % (self.ip,self.status.status)


    def save(self,*args,**kwargs):
        return super(vmware_service_ip,self).save(*args,**kwargs)
    
    def lock(self):
        self.status=vmware_ip_status.objects.get(status='locked')
        #self.save()
    def unlock(self):
        self.status=vmware_ip_status.objects.get(status='available')

class vmware_additional_ip(models.Model):
    ip=models.IPAddressField(unique=True)
    netmask=models.IPAddressField(default='255.255.255.0')
    gateway=models.IPAddressField(blank=True,null=True)
    available_status=vmware_ip_status.objects.get(status_id=0)
    status=models.ForeignKey(vmware_ip_status,default=available_status)
    
    def __unicode__(self):
        return "%s, %s" % (self.ip,self.status.status)


    def save(self,*args,**kwargs):
        return super(vmware_additional_ip,self).save(*args,**kwargs)
    
    def lock(self):
        self.status=vmware_ip_status.objects.get(status='locked')
        #self.save()
    def unlock(self):
        self.status=vmware_ip_status.objects.get(status='available')
        
# vmware machine        
class vmware_machine(models.Model):
    latest_service_request_id=models.IntegerField()
    name=models.CharField(max_length=100,unique=True)
    os_template=models.ForeignKey(vmware_template)
    manage_ip=models.ForeignKey(vmware_manage_ip,unique=True)
    
    service_ip=models.ForeignKey(vmware_service_ip,blank=True,null=True)
    
    additional_ip=models.ForeignKey(vmware_additional_ip,blank=True,null=True)
    
    dns_ip_1=models.IPAddressField(blank=True,null=True)
    dns_ip_2=models.IPAddressField(blank=True,null=True)
    
    user=models.CharField(max_length=30)
    user_branch_bank=models.CharField(max_length=50,blank=True,null=True)
    user_department=models.CharField(max_length=50,blank=True,null=True)
    user_project_group=models.CharField(max_length=50,blank=True,null=True)
    
    manage_username=models.CharField(max_length=50)
    manage_password=models.CharField(max_length=50)
    
    cpu_count=models.IntegerField()
    memory_size_gb=models.IntegerField()
    hdd_size_gb=models.IntegerField()
    
    os=models.ForeignKey(vmware_os_type)
    
    esx=models.ForeignKey(vmware_server)
    vcenter=models.ForeignKey(vmware_vcenter)
    datastore=models.ForeignKey(vmware_datastore)
    
    workgroup=models.CharField(max_length=50,blank=True,null=True)
    
    start_date=models.DateField()
    end_date=models.DateField(blank=True,null=True)
    
    price_per_day=models.IntegerField()
    expenses=models.IntegerField()
    
    status=models.ForeignKey(vmware_machine_status)    
    
    def __unicode__(self):
        return 'VMware: %s' % self.name

class vmware_resource_lock_status(models.Model):
    status=models.CharField(max_length=50)
    
    def __unicode__(self):
        return self.status

class vmware_resource_lock(models.Model):
    state=FSMField(default='request')
    service_request_id=models.IntegerField()
    esx=models.ForeignKey(vmware_server,blank=True,null=True)
    cpu=models.IntegerField(blank=True,null=True)
    mem=models.IntegerField(blank=True,null=True)
    storage_type=models.ForeignKey(vmware_datastore_type,blank=True,null=True)
    disk_space=models.IntegerField(blank=True,null=True)
    data_store=models.ForeignKey(vmware_datastore,blank=True,null=True)
    vmware_manage_ip=models.ForeignKey(vmware_manage_ip,blank=True,null=True)
    vmware_service_ip=models.ForeignKey(vmware_service_ip,blank=True,null=True)
    status=models.ForeignKey(vmware_resource_lock_status)
    
    def __unicode__(self):
        return 'Service request id: %d, %s' % (self.service_request_id,self.status.status)

    
    def save(self,*args,**kwargs):
        return super(vmware_resource_lock,self).save(*args,**kwargs)
        
    #@transition(field=state,source='*',target='freeze',save=True)
    def FreezeResource(self,ChangeStatus=False):
        logger.info('freeze resource')
        try:
            flag=FreezeVMwareLockedResource(esx=self.esx,cpu=self.cpu,mem=self.mem,\
                               storage_type=self.storage_type,\
                               data_store=self.data_store,disk_space=self.disk_space,\
                               manage_ip=self.vmware_manage_ip,service_ip=self.vmware_service_ip)
            """
            if self.status!=vmware_resource_lock_status.objects.get(status='freeze') \
                                                            and ChangeStatus:
                self.status=vmware_resource_lock_status.objects.get(status='freeze')
                self.save()
            """
            return flag
        except Exception,e:
            logger.error('Error in Freezing resource. %s' % e)
            return False
        
######################################################################
#                                                                    #
#                                                                    #
#                  Workflow Engine                                   #
#                                                                    #
#                                                                    #
######################################################################

@receiver(pre_save,sender=vmware_resource_lock,dispatch_uid='lockresource')
def pre_save_vmware_resource_locked(sender,**kwargs):
    #before lock item has been added, status chan
    instance=kwargs.get('instance')
    if instance.id:
        old_vmware_resource_lock=vmware_resource_lock.objects.get(pk=instance.id)
        
        if old_vmware_resource_lock.status.status=='request' and instance.status.status=='freezed':
            logger.info('request to freezed')
            instance.state='freeze'
            logger.info('pre_status: request, post_status: freeze')
            if not instance.FreezeResource():
                instance.state='Freeze Error'
                instance.status=vmware_resource_lock_status.objects.get(status='Error')
            else:
                instance.state='Freezed'
                instance.status=vmware_resource_lock_status.objects.get(status='freezed')
                
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
                if resource_type=='vmware_machine':
                    #create a vmware_machine item, status is deploying
                    try:
                        CreateVMware_machine(instance,service_request)
                    except Exception,e:
                        logger.error('Error in Create vmware_machine. %s' % e)
                
                #set ServiceRequest Status to 'plan to implement'
                service_request.request_status=workflow.models.RequestStatus.objects.get(request_status_id=3)
                service_request.save()
                
        if old_vmware_resource_lock.status.status=='freezed' and instance.status.status=='free':
            #set the resources in this item to available, add the cpu, mem to esx, diskspace
            if instance.esx:
                instance.esx.available_cpu+=instance.cpu
                instance.esx.available_mem_gb+=instance.mem
                instance.esx.save()
            if instance.disk_space:
                if instance.storage_type.type=='internal':
                    instance.esx.available_storage_capacity_gb+=instance.disk_space
                    #esx.save()
                instance.data_store.available_capacity_gb+=instance.disk_space
            if instance.vmware_manage_ip:
                instance.vmware_manage_ip.unlock()
            if instance.vmware_service_ip:
                instance.vmware_service_ip.unlock()
            
            if instance.esx:
                instance.esx.save()
            if instance.disk_space:
                instance.data_store.save()
            if instance.vmware_service_ip:
                instance.vmware_service_ip.save()
            if instance.vmware_manage_ip:
                instance.vmware_manage_ip.save()
         
@receiver(pre_save,sender=vmware_machine,dispatch_uid='vmware_machine_pre_save')
def pre_save_vmware_machine(sender,instance,**kwargs):
    if instance.id:
        vm_status_deploying=vmware_machine_status.objects.get(status_id=1)
        vm_status_ready_to_deploy=vmware_machine_status.objects.get(status_id=0)
        old_instance=vmware_machine.objects.get(pk=instance.id)
        pass

@receiver(post_save,sender=vmware_machine,dispatch_uid='vmware_machine_post_save')
def post_save_vmware_machine(sender,instance,**kwargs):
    #new created, need to deploy
    vm_status_deploying=vmware_machine_status.objects.get(status_id=1)
    vm_status_ready_to_deploy=vmware_machine_status.objects.get(status_id=0)
    vm_status_error_deploy=vmware_machine_status.objects.get(status_id=8)
    if instance.status==vm_status_ready_to_deploy:
        #send to EUAO to provision
        try:
            CreateEUAOTask(instance)
            instance.status=vm_status_deploying
            instance.save()
        except Exception,e:
            logger.error('Error in Create euao task. %s' % e)
            instance.status=vm_status_error_deploy
            instance.save()
    
    if instance.status==vm_status_error_deploy:
        sq_id=instance.latest_service_request_id
        sq=workflow.models.ServiceRequest.objects.get(id=sq_id)
        sq_status_error_deploy=workflow.models.RequestStatus.objects.get(request_status_id=10)
        sq.request_status=sq_status_error_deploy
        sq.save()
    
    if instance.status==vm_status_deploying:
        sq_id=instance.latest_service_request_id
        sq=workflow.models.ServiceRequest.objects.get(id=sq_id)
        sq_status_running=workflow.models.RequestStatus.objects.get(request_status_id=11)
        sq.request_status=sq_status_running
        sq.save()
    
@receiver(post_save,sender=vmware_datastore,dispatch_uid='sync datastore and esx')
def post_save_datastore(sender,instance,**kwargs):
    internal_datastore_type=vmware_datastore_type.objects.get(type='internal')
    if instance.datastore_type==internal_datastore_type:
        #sync to esx
        esx=instance.esx
        esx.total_storage_capacity_gb=instance.total_capacity_gb
        esx.available_storage_capacity_gb=instance.available_capacity_gb
        esx.save()
        