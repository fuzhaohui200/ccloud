# -*- coding: utf-8 -*-
import models
import aix.setting as setting
import aix.add_resource_pool as resource_pool
def init_ip_status():
    ip_available=models.aix_ip_status(status_id=1,status='available')
    ip_available.save()
    ip_locked=models.aix_ip_status(status_id=2,status='locked')
    ip_locked.save()
    ip_used=models.aix_ip_status(status_id=3,status='used')
    ip_used.save()

def init_resource_status():
    resource_available=models.resource_available(available=True)
    resource_available.save()
    resource_unavailable=models.resource_available(available=False)
    resource_unavailable.save()

def init_nim():
    nim=models.nim_server(ip=setting.NIMserver['ip'],
                          username=setting.NIMserver['username'],
                          password=setting.NIMserver['password'],
                          prompt=setting.NIMserver['prompt'])
    nim.save()
    
def init_vio_server():
    vio_1=models.vio_server(name='vio_1',
                            ip=setting.VIOServer1['ip'],
                            username=setting.VIOServer1['username'],
                            password=setting.VIOServer1['password'],
                            prompt=setting.VIOServer1['prompt'])
    
    vio_2=models.vio_server(name='vio_2',
                            ip=setting.VIOServer2['ip'],
                            username=setting.VIOServer2['username'],
                            password=setting.VIOServer2['password'],
                            prompt=setting.VIOServer2['prompt'])
    vio_1.save()
    vio_2.save()

def init_hmc():
    hmc=models.hmc(ip=setting.HMC['ip'],
                   username=setting.HMC['username'],
                   password=setting.HMC['password'],
                   prompt=setting.HMC['prompt'])
    hmc.save()

def init_aix_version():
    for ver in setting.AIX_Version:
        aix_ver=models.aix_version(version=ver['version'],
                                   spot=ver['spot'],
                                   lpp_source=ver['lpp_source'],
                                   mksysb=ver['mksysb'])
        aix_ver.save()

def init_vioclient_status():
    for status in setting.vioclient_status:
        vio_client_status=models.vioclient_status(status_id=status['status_id'],
                                                  status=status['status'])
        vio_client_status.save()

def init():
    init_ip_status()
    init_resource_status()
    init_vio_server()
    init_nim()

#################################################
#  clear table, reset all resource to available #
#################################################
def reset_ip():
    available_status=models.aix_ip_status.objects.get(status_id=1)
    for ip in models.aix_service_ip.objects.all():
        if ip.status!=available_status:
            ip.status=available_status
            ip.save()
    for ip in models.aix_manage_ip.objects.all():
        if ip.status!=available_status:
            ip.status=available_status
            ip.save()

def reset_hdisk():
    available_status=models.resource_available.objects.get(available=True)
    for disk in models.hdisk.objects.all():
        if disk.status !=available_status:
            disk.status=available_status
            disk.save()
def reset_vhost():
    available_status=models.resource_available.objects.get(available=True)
    for vhost_item in models.vhost.objects.all():
        if vhost_item.status !=available_status:
            vhost_item.status=available_status
            vhost_item.save()
            
def reset_aix_server():
    for aixserver in models.aix_server.objects.all():
        aixserver.available_cpu=aixserver.total_cpu
        aixserver.available_mem=aixserver.total_mem
        aixserver.save()

def clear_vio_client():
    for vc in models.vioclient.objects.all():
        vc.delete()

def clear_vio_resource_lock():
    for vcl in models.aix_resource_lock.objects.all():
        vcl.delete()

def clear_all():
    print 'reset ip'
    reset_ip()
    print 'reset hdisk'
    reset_hdisk()
    print 'reset vhost'
    reset_vhost()
    print 'reset aix server'
    reset_aix_server()
    print 'clear vio client'
    clear_vio_client()
    print 'clear locked resource items'
    clear_vio_resource_lock()
    
    reset_aix_server()
    reset_hdisk()
    reset_ip()

def set_test_hdisk(hdisk_count):
    for i in range(hdisk_count):
        m_hdisk=models.hdisk()
        m_hdisk.aix_server=models.aix_server.objects.all()[0]
        hdisk_id=i+2
        m_hdisk.rootvg_lun='hdiskpower%d' % hdisk_id
        m_hdisk.vio_1=models.vio_server.objects.get(name='vio_1')
        m_hdisk.vio_2=models.vio_server.objects.get(name='vio_2')
        m_hdisk.vhost_name='vhost%d' % hdisk_id
        m_hdisk.vtd_name='vioc%d_rootvg' % hdisk_id
        m_hdisk.virtual_scsi_adapter=str(hdisk_id)
        m_hdisk.status=m_hdisk.status_available
        m_hdisk.save()


def set_test_manage_ip(ip_count):
    for i in range(ip_count):
        m_manage_ip=models.aix_manage_ip()
        ip_id=i+30
        m_manage_ip.ip='200.0.52.%d' % ip_id
        m_manage_ip.gateway='200.0.52.100'
        m_manage_ip.netmask='255.255.255.0'
        m_manage_ip.status=m_manage_ip.available_status
        m_manage_ip.save()

def set_test_service_ip(ip_count):
    for i in range(ip_count):
        m_service_ip=models.aix_service_ip()
        ip_id=i+30
        m_service_ip.ip='192.168.35.%d' % ip_id
        m_service_ip.gateway='192.168.35.1'
        m_service_ip.netmask='255.255.255.0'
        m_service_ip.status=m_service_ip.available_status
        m_service_ip.save()

# given str like hdisk#2-10#, return a list from hdisk2 to hdisk10
def get_list_from_str(list_str):
    try:
        li=list_str.split('#')
        a=li[0]
        b=li[1]
        c=li[2]
        result=[]
        for i in range(int(b.split('-')[0]),int(b.split('-')[1])+1):
            result.append('%s%d%s' % (a,i,c))
        return result
    except:
        return []

#read info from add_resource_pool.py to add hdisk
def add_hdisk():
    hdisk_server_list=resource_pool.hdisk
    available_status=models.resource_available.objects.get(available=True)
    for server_item in hdisk_server_list:
        server_name=server_item.get('name')
        hdisk_list=get_list_from_str(server_item.get('hdisk'))
        vhost_list=get_list_from_str(server_item.get('vhost'))
        vtd_name_list=get_list_from_str(server_item.get('vtd_name'))
        virtual_scsi_adapter_list=get_list_from_str(server_item.get('virtual_scsi_adapter'))
        if len(hdisk_list)==len(vhost_list)==len(vtd_name_list)==len(virtual_scsi_adapter_list):
            #add hdisk
            for i in range(len(hdisk_list)):
                if not models.hdisk.objects.filter(rootvg_lun=hdisk_list[i]):
                    hdisk_item=models.hdisk()
                    hdisk_item.rootvg_lun=hdisk_list[i]
                    hdisk_item.aix_server=models.aix_server.objects.get(name=server_name)
                    hdisk_item.vhost_name=vhost_list[i]
                    hdisk_item.vtd_name=vtd_name_list[i]
                    hdisk_item.virtual_scsi_adapter=virtual_scsi_adapter_list[i]
                    hdisk_item.status=available_status
                    hdisk_item.save()
                
        
        
        

#read info from add_resource_pool.py
def add_ip():
    mgr_ip_list_str=resource_pool.aix_manage_ip_list
    mgr_ip_list=[]
    ip_template_split_list=mgr_ip_list_str.split('.')
    start_ip_d=int(ip_template_split_list[3].split('-')[0])
    end_ip_d=int(ip_template_split_list[3].split('-')[1])
    mgr_ip_start_str='%s.%s.%s.' % (ip_template_split_list[0],ip_template_split_list[1],ip_template_split_list[2])
    for i in range(start_ip_d,end_ip_d+1):
        m_manage_ip=models.aix_manage_ip()
        m_manage_ip.ip=mgr_ip_start_str+str(i)
        if not models.aix_manage_ip.objects.filter(ip=m_manage_ip.ip):
            m_manage_ip.gateway=resource_pool.aix_manage_ip_gateway
            m_manage_ip.netmask=resource_pool.aix_manage_ip_mask
            m_manage_ip.status=m_manage_ip.available_status
            m_manage_ip.save()
            
    
    service_ip_list_str=resource_pool.aix_service_ip_list
    service_ip_list=[]
    service_ip_template_split_list=service_ip_list_str.split('.')
    start_ip_d=int(service_ip_template_split_list[3].split('-')[0])
    end_ip_d=int(service_ip_template_split_list[3].split('-')[1])
    service_ip_start_str='%s.%s.%s.' % (service_ip_template_split_list[0],service_ip_template_split_list[1],service_ip_template_split_list[2])
    for i in range(start_ip_d,end_ip_d+1):
        m_service_ip=models.aix_service_ip()
        m_service_ip.ip=service_ip_start_str+str(i)
        if not models.aix_service_ip.objects.filter(ip=m_service_ip.ip):
            m_service_ip.gateway=resource_pool.aix_service_ip_gateway
            m_service_ip.netmask=resource_pool.aix_service_ip_mask
            m_service_ip.status=m_service_ip.available_status
            m_service_ip.save()
        
    
def set_test(count):
    set_test_hdisk(count)
    set_test_manage_ip(count)
    set_test_service_ip(count)

def delete_test_hdisk():
    for hdisk_item in models.hdisk.objects.all():
        hdisk_item.delete()

def delete_test_manage_ip():
    for ip_item in models.aix_manage_ip.objects.all():
        ip_item.delete()

def delete_test_service_ip():
    for ip_item in models.aix_service_ip.objects.all():
        ip_item.delete()
        
def delete_test():
    delete_test_hdisk()
    delete_test_service_ip()
    delete_test_manage_ip()
    