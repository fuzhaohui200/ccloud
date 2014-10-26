from django.db import models
# Create your models here.
from django.db.models.signals import *
from django.dispatch import receiver
from django.contrib.auth.models import User
import datetime
import logging
logger=logging.getLogger('ecms')
from aix.models import aix_server
from aix.models import hdisk_type
from aix.models import hdisk
from aix.models import vhost
from aix.models import aix_service_ip
from aix.models import aix_manage_ip
from aix.models import aix_ip_status
import aix
from aix.aix_init_function import get_list_from_str

# Create your models here.
class hdisk_pool(models.Model):
    rootvg_lun=models.CharField(max_length=200)
    aix_server=models.ForeignKey(aix_server)
    type=models.ForeignKey(hdisk_type)
    add_time=models.DateTimeField(blank=True,null=True)
    
    def __unicode__(self):
        return 'Add %s at %s' % (self.rootvg_lun,self.add_time)
        
    def save(self,*args,**kwargs):
        ''' On save, update timestamps '''
        self.add_time=datetime.datetime.today()
        super(hdisk_pool, self).save(*args, **kwargs)
        
        
class vhost_pool(models.Model):
    vhost_name=models.CharField(max_length=200)
    virtual_scsi_adapter=models.CharField(max_length=200)
    aix_server=models.ForeignKey(aix_server)
    add_time=models.DateTimeField(blank=True,null=True)
    def __unicode__(self):
        return 'Add %s,%s at %s' % (self.vhost_name,self.virtual_scsi_adapter,self.add_time)
    def save(self,*args,**kwargs):
        self.add_time=datetime.datetime.today()
        super(vhost_pool,self).save(*args,**kwargs)
        
        
class aix_service_ip_pool(models.Model):
    ip=models.CharField(max_length=200)
    netmask=models.IPAddressField()
    gateway=models.IPAddressField()
    vlan=models.ForeignKey(aix.models.vlan,related_name='service_ip_vlan')
    add_time=models.DateTimeField(blank=True,null=True)
    def __unicode__(self):
        return 'Add %s,%s at %s' % (self.ip,self.vlan,self.add_time)
    def save(self,*args,**kwargs):
        self.add_time=datetime.datetime.today()
        super(aix_service_ip_pool,self).save(*args,**kwargs)
        
        
class aix_manage_ip_pool(models.Model):
    ip=models.CharField(max_length=200)
    netmask=models.IPAddressField()
    gateway=models.IPAddressField()
    vlan=models.ForeignKey(aix.models.vlan,related_name='manage_ip_vlan')
    add_time=models.DateTimeField(blank=True,null=True)
    def __unicode__(self):
        return 'Add %s,%s at %s' % (self.ip,self.vlan,self.add_time)
    def save(self,*args,**kwargs):
        self.add_time=datetime.datetime.today()
        super(aix_manage_ip_pool,self).save(*args,**kwargs)
        
        
@receiver(post_save,sender=aix_service_ip_pool)
def post_save_aix_service_ip(sender,instance,**kwargs):
    ip_list=get_list_from_str(instance.ip)
    m_netmask=instance.netmask
    m_gateway=instance.gateway
    m_vlan=instance.vlan
    ip_available=aix_ip_status.objects.get(status_id=1)
    for ip_item in ip_list:
        if not aix_service_ip.objects.filter(ip=ip_item):
            aix_service_ip_item=aix_service_ip()
            aix_service_ip_item.ip=ip_item
            aix_service_ip_item.netmask=m_netmask
            aix_service_ip_item.gateway=m_gateway
            aix_service_ip_item.vlan=m_vlan
            aix_service_ip_item.status=ip_available
            aix_service_ip_item.save()
            
@receiver(post_save,sender=aix_manage_ip_pool)
def post_save_aix_manage_ip(sender,instance,**kwargs):
    ip_list=get_list_from_str(instance.ip)
    m_netmask=instance.netmask
    m_gateway=instance.gateway
    m_vlan=instance.vlan
    ip_available=aix_ip_status.objects.get(status_id=1)
    for ip_item in ip_list:
        if not aix_manage_ip.objects.filter(ip=ip_item):
            aix_manage_ip_item=aix_manage_ip()
            aix_manage_ip_item.ip=ip_item
            aix_manage_ip_item.netmask=m_netmask
            aix_manage_ip_item.gateway=m_gateway
            aix_manage_ip_item.vlan=m_vlan
            aix_manage_ip_item.status=ip_available
            aix_manage_ip_item.save()
            
            
            
@receiver(post_save,sender=hdisk_pool)
def post_save_hdisk_pool(sender,instance,**kwargs):
    #add hdisk to resource pool
    rootvg_lun_str=instance.rootvg_lun
    rootvg_lun_list=get_list_from_str(rootvg_lun_str)
    available_status=aix.models.resource_available.objects.get(available=True)
    for rootvg_lun_item in rootvg_lun_list:
        if not hdisk.objects.filter(rootvg_lun=rootvg_lun_item):
            hdisk_item=hdisk()
            hdisk_item.rootvg_lun=rootvg_lun_item
            hdisk_item.aix_server=instance.aix_server
            hdisk_item.status=available_status
            hdisk_item.type=instance.type
            hdisk_item.save()
@receiver(post_save,sender=vhost_pool)
def post_save_vhost_pool(sender,instance,**kwargs):
    vhost_name_list=get_list_from_str(instance.vhost_name)
    virtual_scsi_adapter_list=get_list_from_str(instance.virtual_scsi_adapter)
    if len(vhost_name_list)!=len(virtual_scsi_adapter_list):
        logger.error('Error in add vhost, %s, %s' % (instance.vhost_name,instance.virtual_scsi_adapter))
        return
    else:
        available_status=aix.models.resource_available.objects.get(available=True)
        for i in range(len(vhost_name_list)):
            if not vhost.objects.filter(vhost_name=vhost_name_list[i],aix_server=instance.aix_server) and not vhost.objects.filter(virtual_scsi_adapter=virtual_scsi_adapter_list[i],aix_server=instance.aix_server):
                vhost_item=vhost()
                vhost_item.vhost_name=vhost_name_list[i]
                vhost_item.virtual_scsi_adapter=virtual_scsi_adapter_list[i]
                vhost_item.aix_server=instance.aix_server
                vhost_item.status=available_status
                vhost_item.save()
