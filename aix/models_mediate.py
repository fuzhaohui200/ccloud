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
    location=models.CharField(max_length=50,blank=True,null=True)
    alias=models.CharField(max_length=50,blank=True,null=True)
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
        return 'AIX_Server: %s' % self.name
    
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

class hdisk_10(models.Model):
    rootvg_lun=models.CharField(max_length=100,unique=True)
    aix_server=models.ForeignKey(aix_server)
    vio_1=models.ForeignKey(vio_server,related_name='hdisk_vio_server_1_10',blank=True,null=True)
    vio_2=models.ForeignKey(vio_server,related_name='hdisk_vio_server_2_10',blank=True,null=True)
    hdisk_id=models.CharField(max_length=100,blank=True,null=True)
    vio_client_id=models.CharField(max_length=50,blank=True,null=True)
    vhost_name=models.CharField(max_length=50,unique=True)
    vtd_name=models.CharField(max_length=50,unique=True)
    virtual_scsi_adapter=models.CharField(max_length=10,unique=True)
    status_available=resource_available.objects.get(available=True)
    status=models.ForeignKey(resource_available,default=status_available)

    def __unicode__(self):
        return 'hdisk: %s,%s' % (self.rootvg_lun,self.status)

    def lock(self):
        status_lock=resource_available.objects.get(available=False)
        self.status=status_lock
    def unlock(self):
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

class aix_service_ip_10(models.Model):
    ip=models.IPAddressField(unique=True)
    netmask=models.IPAddressField(default='255.255.255.0')
    gateway=models.IPAddressField(blank=True,null=True)
    available_status=aix_ip_status.objects.get(status_id=1)
    status=models.ForeignKey(aix_ip_status,default=available_status)

    def __unicode__(self):
        return '%s: %s' % (self.ip,self.status)
    
    def lock(self):
        locked_status=aix_ip_status.objects.get(status='locked')
        self.status=locked_status
        
    def unlock(self):
        unlocked_status=aix_ip_status.objects.get(status='available')
        self.status=unlocked_status
        
class aix_manage_ip_10(models.Model):
    ip=models.IPAddressField(unique=True)
    netmask=models.IPAddressField(default='255.255.255.0')
    gateway=models.IPAddressField(blank=True,null=True)
    available_status=aix_ip_status.objects.get(status_id=1)
    status=models.ForeignKey(aix_ip_status,default=available_status)
    #status=models.ForeignKey(aix_ip_status)
    def __unicode__(self):
        return '%s: %s' % (self.ip,self.status)

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

class aix_resource_lock_10(models.Model):
    service_request_id=models.IntegerField()
    aix_server=models.ForeignKey(aix_server,blank=True,null=True)
    cpu=models.IntegerField(blank=True,null=True)
    mem=models.IntegerField(blank=True,null=True)
    aix_service_ip=models.ForeignKey(aix_service_ip,blank=True,null=True)
    aix_manage_ip=models.ForeignKey(aix_manage_ip,blank=True,null=True)
    hdisk=models.ForeignKey(hdisk_10,blank=True,null=True)
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
                                      hdisk=self.hdisk)
           
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
    status=models.ForeignKey(vioclient_status)
    
    def __unicode__(self):
        return 'User: %s, Name:%s, ManageIP:%s, ServiceIP: %s, Status:%s' % (self.belong_to_username,self.name,self.manage_ip.ip,self.service_ip.ip,self.status.status)



class vioclient_10(models.Model):
    belong_to_username=models.CharField(max_length=50)
    latest_service_request_id=models.IntegerField()
    resource_lock_item=models.ForeignKey(aix_resource_lock)
    name=models.CharField(max_length=50,unique=True)
    server=models.ForeignKey(aix_server)
    vioserver_1=models.ForeignKey(vio_server,related_name='vioserver_1_10')
    vioserver_2=models.ForeignKey(vio_server,related_name='vioserver_2_10')
    hdisk=models.ForeignKey(hdisk)

    service_netcard=models.CharField(max_length=10,default=setting.vioclient_netcard.get('service_netcard'))
    manage_netcard=models.CharField(max_length=10,default=setting.vioclient_netcard.get('manage_netcard'))
    service_ip=models.ForeignKey(aix_service_ip,unique=True)
    manage_ip=models.ForeignKey(aix_manage_ip,unique=True)
    
    username=models.CharField(max_length=50,default=setting.vioclient_default_user)
    password=models.CharField(max_length=50,default=setting.vioclient_default_passwd)
    
    nim_server=models.ForeignKey(nim_server)
    os_version=models.ForeignKey(aix_version)
    
    min_procs=models.IntegerField(default=1)
    desired_procs=models.IntegerField()
    max_procs=models.IntegerField(default=16)
    
    min_procs_unit=models.FloatField(default=0.1)
    desired_procs_unit=models.FloatField(default=0.5)
    max_procs_unit=models.FloatField(default=16.0)
    
    min_mem=models.IntegerField(default=1)
    desired_mem=models.IntegerField()
    max_mem=models.IntegerField(default=16)
    
    virtual_eth_adapters=models.CharField(max_length=200,default=setting.vioclient_virtual_eth_adapter)
    #virtual_scsi_adapter=models.CharField(max_length=50,default=setting.vioclient_virtual_scsi_adapter)
    
    status=models.ForeignKey(vioclient_status)
    
    def __unicode__(self):
        return 'User: %s, Name:%s, ManageIP:%s, ServiceIP: %s, Status:%s' % (self.belong_to_username,self.name,self.manage_ip.ip,self.service_ip.ip,self.status.status)

    
