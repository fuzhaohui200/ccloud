# -*- coding: utf-8 -*-

import aix

from aix.models import aix_manage_ip,aix_manage_ip_10
from aix.models import aix_service_ip,aix_service_ip_10
from aix.models import aix_resource_lock,aix_resource_lock_10
from aix.models import hdisk,hdisk_10
from aix.models import hdisk_type
from aix.models import vhost
from aix.models import vioclient,vioclient_10
from aix.models import vlan


#new db
vlan_type_list=[{'name':'manage','description':'管理网段'},
    {'name':'service','description':'服务网段'},]

vlan_list=[{'name':'原有IP管理网段','description':'升级前IP管理网段'},
    {'name':'原有IP服务网段','description':'升级前IP服务网段'}]

hdisk_type_list=[{'name':'原有Hdisk类型','description':'原有Hdisk类型描述'}]

vioclient_type_list=[{'name':'原有vioclient类型','description':'原有vioclient类型描述'}]


def add_vlan_type():
    for item in vlan_type_list:
        vlan_type_item=aix.models.vlan_type()
        vlan_type_item.name=item['name']
        vlan_type_item.description=item['description']
        vlan_type_item.save()

def add_manage_vlan(vlan_id):
    vlan_item=aix.models.vlan()
    vlan_item.name=vlan_list[0]['name']
    vlan_item.description=vlan_list[0]['description']
    vlan_item.vlan_id=vlan_id
    vlan_item.type=aix.models.vlan_type.objects.get(id=1)
    vlan_item.save()

def add_service_vlan(vlan_id):
    vlan_item=aix.models.vlan()
    vlan_item.name=vlan_list[1]['name']
    vlan_item.description=vlan_list[0]['description']
    vlan_item.vlan_id=vlan_id
    vlan_item.type=aix.models.vlan_type.objects.get(id=2)
    vlan_item.save()

def add_hdisk_type():
    hdisk_type_item=aix.models.hdisk_type()
    hdisk_type_item.name=hdisk_type_list[0]['name']
    hdisk_type_item.description=hdisk_type_list[0]['description']
    hdisk_type_item.save()


def add_vioclient_type():
    vioclient_type_item=aix.models.vioclient_type()
    vioclient_type_item.name=vioclient_type_list[0]['name']
    vioclient_type_item.description=vioclient_type_list[0]['description']
    vioclient_type_item.default_service_vlan=aix.models.vlan.objects.get(id=2)
    vioclient_type_item.default_manage_vlan=aix.models.vlan.objects.get(id=1)
    vioclient_type_item.default_hdisk_type=aix.models.hdisk_type.objects.get(id=1)
    vioclient_type_item.save()


def add_vhost_from_hdisk_10():
    for old_hdisk_item in hdisk_10.objects.all():
        vhost_item=vhost()
        vhost_item.vhost_name=old_hdisk_item.vhost_name
        vhost_item.virtual_scsi_adapter=old_hdisk_item.virtual_scsi_adapter
        vhost_item.aix_server=old_hdisk_item.aix_server
        vhost_item.status=old_hdisk_item.status
        vhost_item.save()

def migrate_hdisk():
    for old_hdisk_item in hdisk_10.objects.all():
        hdisk_item=hdisk()
        hdisk_item.id=old_hdisk_item.id
        hdisk_item.rootvg_lun=old_hdisk_item.rootvg_lun
        hdisk_item.aix_server=old_hdisk_item.aix_server
        hdisk_item.vio_1=old_hdisk_item.vio_1
        hdisk_item.vio_2=old_hdisk_item.vio_2
        hdisk_item.hdisk_id=old_hdisk_item.hdisk_id
        hdisk_item.vio_client_id=old_hdisk_item.vio_client_id
        hdisk_item.vhost=vhost.objects.get(vhost_name=old_hdisk_item.vhost_name)
        hdisk_item.vtd_name=old_hdisk_item.vtd_name
        hdisk_item.type=hdisk_type.objects.get(id=1)
        hdisk_item.status=old_hdisk_item.status
        hdisk_item.save()
        

def migrate_manage_ip():
    for old_manage_ip in aix_manage_ip_10.objects.all():
        manage_ip_item=aix_manage_ip()
        manage_ip_item.id=old_manage_ip.id
        manage_ip_item.ip=old_manage_ip.ip
        manage_ip_item.netmask=old_manage_ip.netmask
        manage_ip_item.gateway=old_manage_ip.gateway
        manage_ip_item.vlan=vlan.objects.get(id=1)
        manage_ip_item.status=old_manage_ip.status
        manage_ip_item.save()
        

def migrate_service_ip():
    for old_service_ip in aix_service_ip_10.objects.all():
        service_ip_item=aix_service_ip()
        service_ip_item.id=old_service_ip.id
        service_ip_item.ip=old_service_ip.ip
        service_ip_item.netmask=old_service_ip.netmask
        service_ip_item.gateway=old_service_ip.gateway
        service_ip_item.vlan=vlan.objects.get(id=2)
        service_ip_item.status=old_service_ip.status
        service_ip_item.save()

def migrate_resource_lock():
    for old_resource_lock in aix_resource_lock_10.objects.all():
        resource_lock_item=aix_resource_lock()
        resource_lock_item.service_request_id=old_resource_lock.service_request_id
        resource_lock_item.aix_server=old_resource_lock.aix_server
        resource_lock_item.cpu=old_resource_lock.cpu
        resource_lock_item.mem=old_resource_lock.mem
        resource_lock_item.aix_service_ip=old_resource_lock.aix_service_ip
        resource_lock_item.aix_manage_ip=old_resource_lock.aix_manage_ip
        resource_lock_item.hdisk=old_resource_lock.hdisk.rootvg_lun
        m_vhost_name=hdisk_10.objects.get(rootvg_lun=resource_lock_item.hdisk).vhost_name
        resource_lock_item.vhost=vhost.objects.get(vhost_name=m_vhost_name)
        resource_lock_item.status=old_resource_lock.status
        resource_lock_item.save()

def migrate_vioclient():
    for old_vioclient in vioclient_10.objects.all():
        vioclient_item=vioclient()
        vioclient_item.id=old_vioclient.id
        vioclient_item.belong_to_username=old_vioclient.belong_to_username
        vioclient_item.latest_service_request_id=old_vioclient.latest_service_request_id
        vioclient_item.resource_lock_item=old_vioclient.resource_lock_item
        vioclient_item.name=old_vioclient.name
        vioclient_item.server=old_vioclient.server
        vioclient_item.vioserver_1=old_vioclient.vioserver_1
        vioclient_item.vioserver_2=old_vioclient.vioserver_2
        vioclient_item.hdisk=old_vioclient.hdisk.rootvg_lun
        
        m_vhost_name=hdisk_10.objects.get(rootvg_lun=vioclient_item.hdisk).vhost_name
        vioclient_item.vhost=vhost.objects.get(vhost_name=m_vhost_name)
        
        vioclient_item.service_netcard=old_vioclient.service_netcard
        vioclient_item.manage_netcard=old_vioclient.manage_netcard
        vioclient_item.service_ip=old_vioclient.service_ip
        vioclient_item.manage_ip=old_vioclient.manage_ip
        vioclient_item.username=old_vioclient.username
        vioclient_item.password=old_vioclient.password
        vioclient_item.nim_server=old_vioclient.nim_server
        vioclient_item.os_version=old_vioclient.os_version
        vioclient_item.min_procs=old_vioclient.min_procs
        vioclient_item.desired_procs=old_vioclient.desired_procs
        vioclient_item.max_procs=old_vioclient.max_procs
        vioclient_item.min_procs=old_vioclient.min_procs
        vioclient_item.desired_procs_unit=old_vioclient.desired_procs_unit
        vioclient_item.max_procs_unit=old_vioclient.max_procs_unit
        vioclient_item.min_procs_unit=old_vioclient.min_procs_unit
        vioclient_item.desired_mem=old_vioclient.desired_mem
        vioclient_item.max_mem=old_vioclient.max_mem
        vioclient_item.min_mem=old_vioclient.min_mem
        vioclient_item.virtual_eth_adapters=old_vioclient.virtual_eth_adapters
        vioclient_item.status=old_vioclient.status
        vioclient_item.save()
    
 
# command function
def add_table(manage_vlan_id,service_vlan_id):
    add_hdisk_type()
    add_vlan_type()
    add_manage_vlan(manage_vlan_id)
    add_service_vlan(service_vlan_id)
    add_vioclient_type()

def migrate():
    add_vhost_from_hdisk_10()
    migrate_hdisk()
    migrate_service_ip()
    migrate_manage_ip()
    migrate_resource_lock()
    migrate_vioclient()

