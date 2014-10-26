from django.contrib.auth.models import User
import logging
logger=logging.getLogger('ecms')

from vmware.models import vmware_os_type,vmware_template,vmware_vcenter,vmware_server,vmware_datastore_type,vmware_datastore,vmware_datacenter,vmware_machine_status,vmware_ip_status,vmware_manage_ip,vmware_service_ip,vmware_additional_ip,vmware_machine,vmware_resource_lock_status,vmware_resource_lock
from time import sleep
from ecms.commonfunction import *
import workflow.setting as setting
import workflow
from workflow.description import *
from aix.models import aix_server
from aix.models import hdisk
from aix.models import aix_service_ip
from aix.models import aix_manage_ip
from aix.models import aix_ip_status
from aix.models import aix_version
from aix.models import aix_resource_lock
from aix.models import aix_resource_lock_status
from aix.models import vioclient
from aix.models import vioclient_status
from aix.models import resource_available

from aix.models import vioclient_type
from aix.models import vhost
from aix.models import vlan
from aix.models import hdisk_type

import aix.setting as aix_setting
import EUAO.models
from ecms.EThread import EThread
#Check User quota available
"""
    usage:
        from workflow.models import *
        request_type=RequestType.objects.get(request_type_id=1)
        request_parameter={'type':'vmware_machine','cpu':1,'mem':3}
        CheckUserQuotaAvailable('ces',request_type,request_parameter)
    return :
        True
        False
"""
def CheckUserQuotaAvailable(username,request_type,request_parameter):
    user=User.objects.get(username=username)
    #show how to get the additional field
    #logger.info('User Company: %s' % user.get_profile().company)
    
    #request_type_id=1: apply for a resource
    logger.debug('Checking user quota:')
    if request_type.request_type_id==1:
        try:
            resource_type=request_parameter.get('type')
            if resource_type=='vmware_machine':
                logger.debug('vmware_machine')
                cpu=request_parameter.get('cpu')
                mem=request_parameter.get('mem')
                logger.debug('cpu %d mem %d' % (cpu,mem))
                user_profile=user.get_profile()
                logger.debug(user_profile.vmware_cpu_quota)
                logger.debug(user_profile.vmware_cpu_used)
                if user_profile.vmware_cpu_quota-user_profile.vmware_cpu_used>=cpu and\
                user_profile.vmware_mem_quota-user_profile.vmware_mem_used>=mem and\
                user_profile.vmware_machine_count_quota>\
                user_profile.vmware_machine_count_used:
                    user_profile.vmware_cpu_used+=cpu
                    user_profile.vmware_mem_used+=mem
                    user_profile.vmware_machine_count_used+=1
                    user_profile.save()
                    return True
                else:
                    logger.info("request resource over %s quota." % user.username)
                    logger.info("request_type: %s" % request_type)
                    logger.info("request_parameter: %s" % request_parameter)
                    return False
            elif resource_type=='aix':
                cpu=request_parameter.get('cpu')
                mem=request_parameter.get('mem')
                logger.debug('Request cpu: %d, mem: %d' % (cpu,mem))
                user_profile=user.get_profile()
                if user_profile.aix_cpu_quota-user_profile.aix_cpu_used>=cpu and\
                user_profile.aix_mem_quota-user_profile.aix_mem_used>=mem and\
                user_profile.aix_count_quota>\
                user_profile.aix_count_used:
                    user_profile.aix_cpu_used+=cpu
                    user_profile.aix_mem_used+=mem
                    user_profile.aix_count_used+=1
                    user_profile.save()
                    logger.debug('Request within quota.')
                    return True
                else:
                    logger.info("request resource over %s quota." % user.username)
                    logger.info("request_type: %s" % request_type)
                    logger.info("request_parameter: %s" % request_parameter)
                    return False
            else:
                logger.error("request type: %s not allowed" % request_type)
                return False
        except Exception,e:
            logger.error("Request key/value error: %s." % e)
            logger.error("request_type: %s" % request_type)
            logger.error("request_parameter: %s" % request_parameter)
            return False
    #request_type_id=2: change a resource
    elif request_type.request_type_id==2:
        return True
    #request_type_id=3: recycle a resource
    elif request_type.request_type_id==3:
        return True
    else:
        return False
    
# Check Resource Pool
"""
    usage:
        from workflow.workflow_function import *
        
        request_parameter2={'cpu': 16, 'mem': 34, 'type': 'vmware_machine', 'os_type':'Linux-suse11sp1','vmware_machine_store_type':'external'}
        CheckResourcePoolAvailable(3,request_parameter2)
        False


    
"""
def CheckResourcePoolAvailable(service_request_id,request_parameter,**kwargs):
    logger.debug('Check ResourcePool Available')
    try:
        resource_type=request_parameter.get('type')
        if resource_type=='vmware_machine':
            #Check esx: vmware_server
            try:
                cpu=request_parameter.get('cpu')
                mem=request_parameter.get('mem')
                logger.debug('cpu: %d, mem: %d' % (cpu,mem))
            except Exception,e:
                logger.error('request_parameter: %s error' % request_parameter)
                return False
            #decend order by available resource, so we choose the largest one firstly
            m_vmware_servers=vmware_server.objects.\
                            order_by('-available_storage_capacity_gb').\
                            order_by('-available_cpu').\
                            order_by('-available_mem_gb')
            if len(m_vmware_servers)<=0:
                logger.info('No vmware server in resource pool.')
                return False
            
            esx_available=False
            #cpu, mem
            data_store_type=request_parameter.get('vmware_machine_store_type','external')
            
            disk_require=0
            try:
                m_vm_os_type=vmware_os_type.objects.get(os_concat=\
                                                      request_parameter.get('os_type'))
                m_vm_template=vmware_template.objects.get(os_type=m_vm_os_type)
                disk_require=m_vm_template.disk_space
            except Exception,e:
                logger.error('Error os_type in request parameter: %s' % request_parameter)
                logger.error(e)
                return False
            
            for esx in m_vmware_servers:
                if data_store_type=='external':
                    if esx.available_cpu>=cpu and esx.available_mem_gb>mem:
                        esx_available=True
                        m_esx_selected=esx
                    else:
                        logger.debug('cpu or mem not available')
                        return False
                elif data_store_type=='internal':
                    if esx.available_cpu>=cpu and esx.available_mem_gb>mem and esx.available_storage_capacity_gb>disk_require:
                        esx_available=True
                        m_esx_selected=esx
                else:
                    logger.error('Datastore type error: %s' % data_store_type)
                
            #Check datastore: vmware_datastore
            #disk space check
            
            datastore_available=False
            m_datastore_selected=None
            
            if data_store_type=='internal':
                #use the datastore in the esx
                if m_esx_selected.available_storage_capacity_gb>disk_require:
                    m_datastore_selected=vmware_datastore.objects.get(esx=m_esx_selected)
                    if m_datastore_selected.available_capacity_gb>disk_require:
                        datastore_available=True
                else:
                    logger.debug('datastore in esx %s not available.' % m_esx_selected)
                    return False
            elif data_store_type=='external':
                #use the external datastore
                datastore_available=False
                datastores=vmware_datastore.objects.order_by('-available_capacity_gb')
                for data_store in datastores:
                    if data_store.available_capacity_gb>disk_require:
                        datastore_available=True
                        m_datastore_selected=data_store
            
                logger.debug("esx: %s, datastore: %s" % (esx_available,datastore_available))
            else:
                logger.error('Must assign the vmware_machine_store_type')
                return False
            
            #ip
            ip_available=False
            ip_available_status=vmware_ip_status.objects.get(status='available')
            #Service IP
            service_ip=vmware_service_ip.objects.filter(status=ip_available_status).\
                                order_by('id')
            manage_ip=vmware_manage_ip.objects.filter(status=ip_available_status).\
                                order_by('id')
            if len(service_ip)>0 and len(manage_ip)>0:
                service_ip_selected=service_ip[0]
                manage_ip_selected=manage_ip[0]
                ip_available=True
            logger.debug('IP available: %s' % ip_available)
            if esx_available and datastore_available and ip_available:
                Add_LockResources(service_request_id=service_request_id,\
                                    resource_type=resource_type,\
                                    vmware_server=m_esx_selected,\
                                    manage_ip=manage_ip_selected,\
                                    service_ip=service_ip_selected,\
                                    data_store_type=data_store_type,\
                                    data_store=m_datastore_selected,\
                                    cpu=cpu,\
                                    mem=mem,\
                                    disk_space=disk_require)
                
                lock_resource_item=vmware_resource_lock.objects.get(service_request_id=service_request_id)
                if lock_resource_item.status==vmware_resource_lock_status.objects.get(status='freezed'):
                    return True
                else:
                    logger.error('Lock Resource error: %s' % lock_resource_item.status.status)
                    return False
            else:
                logger.error('esx_available: %s, datastore_available: %s' \
                             % (esx_available,datastore_available))
                return False
            
        elif resource_type=='aix':
            aix_server_available=False
            ip_available=False
            hdisk_available=False
            vhost_available=False
            aix_version_available=False
            
            #common mode, expert mode
            mode=request_parameter.get('mode')
            
            #common mode: choose the vioclient type, and others depends on the vioclient type 
            if mode=='common':
                vioclient_type_id=''
                try:
                    vioclient_type_id=request_parameter.get('vioclient_type')
                except Exception,e:
                    logger.error('request_parameter: %s error' % request_parameter)
                    logger.debug(trace_back())
                    return False
                m_vioclient_type=vioclient_type.objects.get(id=vioclient_type_id)
                logger.debug('vioclient type: %s' % m_vioclient_type)
                m_manage_vlan=m_vioclient_type.default_manage_vlan
                m_service_vlan=m_vioclient_type.default_service_vlan
                m_hdisk_type=m_vioclient_type.default_hdisk_type
                
            #expert mode, specify all the resource type
            if mode=='expert':
                manage_vlan_item_id=''
                service_vlan_item_id=''
                hdisk_type_id=''
                try:
                    manage_vlan_item_id=request_parameter.get('manage_vlan_item_id')
                    service_vlan_item_id=request_parameter.get('service_vlan_item_id')
                    hdisk_type_id=request_parameter.get('hdisk_type_id')
                except Exception,e:
                    logger.error('request_parameter: %s error' % request_parameter)
                    logger.debug(trace_back())
                    return False
                m_manage_vlan=vlan.objects.get(id=manage_vlan_item_id)
                m_service_vlan=vlan.objects.get(id=service_vlan_item_id)
                m_hdisk_type=hdisk_type.objects.get(id=hdisk_type_id)
            
            #Check server: aix_server
            try:
                cpu=request_parameter.get('cpu')
                mem=request_parameter.get('mem')
                logger.debug('cpu: %d, mem: %d' % (cpu,mem))
            except Exception,e:
                logger.error('request_parameter: %s error' % request_parameter)
                logger.debug(trace_back())
                return False
            #decend order by available resource, so we choose the largest one firstly
            m_aix_servers=aix_server.objects.order_by('-available_cpu').\
                                order_by('-available_mem')
            
            if len(m_aix_servers)<=0:
                logger.info('No aix server in resource pool.')
                return False
            
            available_status=resource_available.objects.get(available=True)
            check_aix_has_available_hdisk=lambda l_aix_server_item,l_hdisk_type:len(hdisk.objects.filter(aix_server=l_aix_server_item,status=available_status,type=l_hdisk_type))>0
            
            for aix_server_item in m_aix_servers:
                logger.debug('available cpu: %d, available mem: %d' % (aix_server_item.available_cpu,aix_server_item.available_mem))
                if cpu<=aix_server_item.available_cpu and mem<=aix_server_item.available_mem and check_aix_has_available_hdisk(aix_server_item,m_hdisk_type):
                    m_aix_server_selected=aix_server_item
                    aix_server_available=True
                    break
            
            #hdisk
            #multiple hdisk
            try:
                hdisk_amout=int(request_parameter.get('hdisk_amount'))
            except Exception,e:
                logger.error('hdisk_amout error: %s' % request_parameter)
                return False
            
            hdisks=hdisk.objects.filter(status=available_status,aix_server=m_aix_server_selected,type=m_hdisk_type)
            if len(hdisks)<=hdisk_amout-1:
                logger.info('No hdisk in resource pool.')
                return False
            
            hdisks_selected=hdisks[:hdisk_amout]
            hdisks_selected_str=''
            for hdisks_selected_item in hdisks_selected[:-1]:
                hdisks_selected_str+=hdisks_selected_item.rootvg_lun+','
            hdisks_selected_str+=hdisks_selected[-1].rootvg_lun
            hdisk_available=True
            
            #vhost
            #one vhost for each vioclient
            vhosts=vhost.objects.filter(status=available_status,aix_server=m_aix_server_selected)
            if len(vhosts)<=0:
                logger.info('No vhost available on server %s in resource pool.' % m_aix_server_selected)
                return False
            vhost_selected=vhosts[0]
            vhost_available=True
            
            ip_available_status=aix_ip_status.objects.get(status='available')
            service_ips=aix_service_ip.objects.filter(status=ip_available_status,vlan=m_service_vlan)
            if len(service_ips)<=0:
                logger.info('No aix service ip of vlan %s available' % m_service_vlan)
                return False
            else:
                service_ip_selected=service_ips[0]
                logger.debug('service ip: %s' % service_ip_selected)
                
            manage_ips=aix_manage_ip.objects.filter(status=ip_available_status,vlan=m_manage_vlan)
            if len(manage_ips)<=0:
                logger.info('No aix manage ip available')
                return False
            else:
                manage_ip_selected=manage_ips[0]
                logger.debug('manage ip: %s' % manage_ip_selected)
                ip_available=True
            
            try:
                str_aix_version=request_parameter.get('os_type')
            except Exception,e:
                logger.error('Error os_type in request parameter: %s' % request_parameter)
                logger.error(e)
                return False
            
            try:
                
                m_aix_version=aix_version.objects.get(version=str_aix_version)
                aix_version_available=True
            except Exception,e:
                logger.error('os version: %s not supported yet.' % str_aix_version)
                logger.error(e)
                return False
            
        
            
            if aix_server_available and ip_available and hdisk_available and vhost_available and aix_version_available:
                logger.debug('Add lock resource.')
                try:
                    Add_LockResources(service_request_id=service_request_id,\
                                        resource_type=resource_type,\
                                        aix_server=m_aix_server_selected,\
                                        manage_ip=manage_ip_selected,\
                                        service_ip=service_ip_selected,\
                                        hdisks=hdisks_selected_str,\
                                        vhost=vhost_selected,\
                                        cpu=cpu,\
                                        mem=mem)
                except Exception,e:
                    logger.error('Error in Add aix resource lock item.')
                    logger.debug(trace_back())
                    return False
                    
                lock_resource_item=aix_resource_lock.objects.get(service_request_id=service_request_id)
                if lock_resource_item.status==aix_resource_lock_status.objects.get(status='freezed'):
                    return True
                else:
                    logger.error('Lock Resource error: %s' % lock_resource_item.status.status)
                    return False
            else:
                logger.error('Available: aix server: %s, ip: %s, hdisk: %s, vhost: %s, aix version: %s' \
                             % (aix_server_available,ip_available,hdisk_available,vhost_available,aix_version_available))
                return False
        elif resource_type=='HP':
            logger.error("Request resource type: %s not support yet." % resource_type)
            return False            
        else:
            logger.error("Request resource type: %s not support yet." % resource_type)
            return False
    except Exception,e:
        logger.error("Error in Check resource pool: %s" % e)
        logger.debug(trace_back())
        return False

def check_vm_name(vm_name):
    try:
        vm=vmware_machine.objects.get(name=vm_name)
        if vm:
            return True
        else:
            return False
    except Exception,e:
        return False

def check_aix_name(aix_name):
    try:
        aix=vioclient.objects.get(name=aix_name)
        if aix:
            return True
        else:
            return False
    except Exception,e:
        return False


def Add_LockResources(**kwargs):
    service_request_id=kwargs.get('service_request_id')
    resource_type=kwargs.get('resource_type')
    
    if resource_type=='vmware_machine':
        try:
            vmware_server=kwargs.get('vmware_server')
            cpu=kwargs.get('cpu')
            mem=kwargs.get('mem')
            manage_ip=kwargs.get('manage_ip')
            service_ip=kwargs.get('service_ip')
            data_store_type=kwargs.get('data_store_type')
            disk_space=kwargs.get('disk_space')
            
            lockVMwareResource=vmware_resource_lock()
            lockVMwareResource.service_request_id=service_request_id
            lockVMwareResource.esx=vmware_server
            lockVMwareResource.cpu=cpu
            lockVMwareResource.mem=mem
            lockVMwareResource.vmware_manage_ip=manage_ip
            lockVMwareResource.vmware_service_ip=service_ip
            lockVMwareResource.storage_type=vmware_datastore_type.objects.get(type=data_store_type)
            data_store=kwargs.get('data_store')
            lockVMwareResource.data_store=data_store
            lockVMwareResource.disk_space=disk_space
            
            lockVMwareResource.status=vmware_resource_lock_status.objects.get(status='request')
            lockVMwareResource.save()
            lockVMwareResource.status=vmware_resource_lock_status.objects.get(status='freezed')
            lockVMwareResource.save()
        except Exception,e:
            logger.error('Error in Add lock resource. %s' % e)
    
    elif resource_type=='aix':
        try:
            a_service_request_id=kwargs.get('service_request_id')
            a_aix_server=kwargs.get('aix_server')
            a_manage_ip=kwargs.get('manage_ip')
            a_service_ip=kwargs.get('service_ip')
            a_hdisks=kwargs.get('hdisks')
            a_vhost=kwargs.get('vhost')
            a_cpu=kwargs.get('cpu')
            a_mem=kwargs.get('mem')
        except Exception,e:
            logger.error('Error in lock resource parameters: %s' % kwargs)
            return
        
        try:    
            aix_resource=aix_resource_lock()
            aix_resource.service_request_id=a_service_request_id
            aix_resource.aix_server=a_aix_server
            aix_resource.cpu=a_cpu
            aix_resource.mem=a_mem
            aix_resource.aix_service_ip=a_service_ip
            aix_resource.aix_manage_ip=a_manage_ip
            aix_resource.hdisk=a_hdisks
            aix_resource.vhost=a_vhost
            aix_resource.status=aix_resource_lock_status.objects.get(status='request')
            aix_resource.save()
            aix_resource.status=aix_resource_lock_status.objects.get(status='freezed')
            aix_resource.save()
        except Exception,e:
            logger.error('Error in locking aix resource: %s' % kwargs)
            return
    else:
        logger.error('resource type: %s not support.' % resource_type)
        return
                    
def ChangeUserQuotaUsage(username,request_type,request_parameter,**kwargs):
    user=User.objects.get(username=username)
    revoke_flag=kwargs.get('revoke',False)
    if not revoke_flag:
        if request_type.request_type_id==1:
            try:
                resource_type=request_parameter.get('type')
                if resource_type=='vmware_machine':
                    cpu=request_parameter.get('cpu')
                    mem=request_parameter.get('mem')
                    user_profile=user.get_profile()
                    user_profile.vmware_cpu_used+=cpu
                    user_profile.vmware_mem_used+=mem
                    user_profile.vmware_machine_count_used+=1
                    user_profile.save()
                if resource_type=='aix':
                    cpu=request_parameter.get('cpu')
                    mem=request_parameter.get('mem')
                    user_profile=user.get_profile()
                    user_profile.aix_cpu_used+=cpu
                    user_profile.aix_mem_used+=mem
                    user_profile.aix_count_used+=1
                    user_profile.save()
            except Exception,e:
                logger.error('Error in Changing user quota. %s' % e)
                logger.debug(trace_back())
    else:
        logger.debug('Revoke user quota.')
        if request_type.request_type_id==1:
            try:
                resource_type=request_parameter.get('type')
                if resource_type=='vmware_machine':
                    cpu=request_parameter.get('cpu')
                    mem=request_parameter.get('mem')
                    user_profile=user.get_profile()
                    user_profile.vmware_cpu_used-=cpu
                    if user_profile.vmware_cpu_used<0:
                        logger.error('User quota info error: vmware_cpu_used:%d' % user_profile.vmware_cpu_used)
                        user_profile.vmware_cpu_used=0
                    user_profile.vmware_mem_used-=mem
                    if user_profile.vmware_mem_used<0:
                        logger.error('User quota info error: vmware_mem_used:%d' % user_profile.vmware_mem_used)
                        user_profile.vmware_mem_used=0
                    user_profile.vmware_machine_count_used-=1
                    if user_profile.vmware_machine_count_used<0:
                        logger.error('User quota info error: vmware_machine_count_used:%d' % user_profile.vmware_machine_count_used)
                        user_profile.vmware_machine_count_used=0
                    
                    user_profile.save()
                if resource_type=='aix':
                    cpu=request_parameter.get('cpu')
                    mem=request_parameter.get('mem')
                    user_profile=user.get_profile()
                    user_profile.aix_cpu_used-=cpu
                    if user_profile.aix_cpu_used<0:
                        logger.error('User quota info error: aix_cpu_used:%d' % user_profile.aix_cpu_used)
                        #user_profile.aix_cpu_used=0
                    user_profile.aix_mem_used-=mem
                    if user_profile.aix_mem_used<0:
                        logger.error('User quota info error: aix_mem_used:%d' % user_profile.aix_mem_used)
                        #user_profile.aix_mem_used=0
                    user_profile.aix_count_used-=1
                    if user_profile.aix_count_used<0:
                        logger.error('User quota info error: aix_count_used:%d' % user_profile.aix_count_used)
                        #user_profile.aix_count_used=0
                    user_profile.save()
            except Exception,e:
                logger.error('Error in Changing user quota. %s' % e)
                logger.debug(trace_back())
                
def CheckResourceBelongToUser(username,request_parameter,**kwargs):
    user=User.objects.get(username=username)
    try:
        resource_type=request_parameter.get('type')
        if resource_type=='vmware_machine':
            vm_name=request_parameter.get('vm')
            logger.debug('CheckResourceBelongToUser not support vmware_machine yet.')
            return False
        elif resource_type=='aix':
            request_vioclient_name=request_parameter.get('name')
            try:
                vioclient_item=vioclient.objects.get(name=request_vioclient_name)
                if username==vioclient_item.belong_to_username:
                    return True
                else:
                    return False
            except Exception,e:
                logger.info("""Can't find request vioclient: %s""" % request_vioclient_name)
                logger.debug(trace_back())
                return False
            
    except Exception,e:
        logger.error('Error in Check reousece belong to user. %s' % e)
        logger.debug(trace_back())
        return False
                        

def CreateEUAOTaskFromServiceRequest(service_request_item,**kwargs):
    logger.debug('CreateEUAOTaskFromServiceRequest')
    m_request_parameter=service_request_item.request_parameter
    try:
        m_request_parameter=eval(m_request_parameter)
        if service_request_item.request_type.request_type_id==3:
            if m_request_parameter.get('type')=='aix':
                
                #recycle an aix
                vioclient_name=m_request_parameter.get('name')
                vioclient_item=vioclient.objects.get(name=vioclient_name)
                
                vioclient_item=vioclient.objects.get(name=vioclient_name)
                vioclient_status_deleting=vioclient_status.objects.get(status_id=3)
                vioclient_item.status=vioclient_status_deleting
                vioclient_item.save()
            
                service_request_id=service_request_item.id
                
                task_space=EUAO.models.euao_service_space.objects.get(name='ControlAIX')
                function=EUAO.models.euao_service_function.objects.get(name='RemoveWholeAIX')
                
                est_exec_time=kwargs.get('est_exec_time',None)
                plan_execute_time=kwargs.get('plan_execute_time',None)
                
                m_aix_server=vioclient_item.server
                m_hmc=m_aix_server.hmc_server
                m_nim=vioclient_item.nim_server
                m_vio_1=vioclient_item.vioserver_1
                m_vio_2=vioclient_item.vioserver_2
                
                #m_hdisk=vioclient_item.hdisk
                
                HMC_IP=m_hmc.ip
                HMC_user=m_hmc.username
                HMC_passwd=m_hmc.password
                HMCServerName=m_aix_server.name
                VIOClientName='%s_%s' % (vioclient_item.belong_to_username,vioclient_name)
                HMC_ssh_port=aix_setting.hmc_default_port
                HMC_cmd_prompt=m_hmc.prompt
                NIM_IP=m_nim.ip
                NIM_username=m_nim.username
                NIM_passwd=m_nim.password
                ServerHostName=vioclient_name
                NIM_port=aix_setting.nimserver_default_port
                NIM_prompt=m_nim.prompt
                VIOServerIP_1=m_vio_1.ip
                VIOServerUsername_1=m_vio_1.username
                VIOServerPasswd_1=m_vio_1.password
                
                hdisks_list_str=vioclient_item.hdisk
                hdisks_list=hdisks_list_str.split(',')
                VTD_name_list_str=''
                for hdisk_item_str in hdisks_list:
                    hdisk_item=hdisk.objects.get(rootvg_lun=hdisk_item_str)
                    VTD_name_list_str+=hdisk_item.vtd_name
                    VTD_name_list_str+=','
                VTD_name_list_str=VTD_name_list_str[:-1]
                #VTD_name=m_hdisk.vtd_name
                
                VIOServerPort_1=aix_setting.vioserver_default_port
                VIOCmd_prompt_1=m_vio_1.prompt
                VIOServerIP_2=m_vio_2.ip
                VIOServerUsername_2=m_vio_2.username
                VIOServerPasswd_2=m_vio_2.password
                VIOServerPort_2=aix_setting.vioserver_default_port
                VIOCmd_prompt_2=m_vio_2.prompt
                
                
                euao_task_parameter="""HMC_IP='%s',HMC_user='%s',HMC_passwd='%s',HMCServerName='%s',VIOClientName='%s',HMC_ssh_port='%s',HMC_cmd_prompt='%s',NIM_IP='%s',NIM_username='%s',NIM_passwd='%s',ServerHostName='%s',NIM_port='%s',NIM_prompt='%s',VIOServerIP_1='%s',VIOServerUsername_1='%s',VIOServerPasswd_1='%s',VTD_name='%s',VIOServerPort_1='%s',VIOCmd_prompt_1='%s',VIOServerIP_2='%s',VIOServerUsername_2='%s',VIOServerPasswd_2='%s',VIOServerPort_2='%s',VIOCmd_prompt_2='%s'""" % (HMC_IP,HMC_user,HMC_passwd,HMCServerName,VIOClientName,HMC_ssh_port,HMC_cmd_prompt,NIM_IP,NIM_username,NIM_passwd,ServerHostName,NIM_port,NIM_prompt,VIOServerIP_1,VIOServerUsername_1,VIOServerPasswd_1,VTD_name_list_str,VIOServerPort_1,VIOCmd_prompt_1,VIOServerIP_2,VIOServerUsername_2,VIOServerPasswd_2,VIOServerPort_2,VIOCmd_prompt_2)
                
                
                euao_task_status_created=EUAO.models.task_status.objects.get(name='created')
                
                task_target_type=EUAO.models.target_type.objects.get(name='aix_vioclient')
                target_instance_number=vioclient_item.id
                euao_task=EUAO.models.task(service_request_id=service_request_id,\
                                        task_space=task_space,\
                                        function=function,\
                                        parameters=euao_task_parameter,\
                                        estimated_execute_time=est_exec_time,\
                                        plan_execute_time=plan_execute_time,\
                                        status=euao_task_status_created,\
                                        target_type=task_target_type,\
                                        target_instance_number=target_instance_number)
            
                euao_task.save()
                        
        elif service_request_item.request_type.request_type_id==2:
            #modify resource
            if m_request_parameter.get('type')=='aix':
                operation_name=m_request_parameter.get('operation')
                if operation_name=='poweron' \
                                  or operation_name=='poweroff' \
                                  or operation_name=='reset':

                    vioclient_name=m_request_parameter.get('name')
                    vioclient_item=vioclient.objects.get(name=vioclient_name)
                    vioclient_status_adjusting=vioclient_status.objects.get(status_id=2)
                    vioclient_item.status=vioclient_status_adjusting
                    vioclient_item.save()
                    service_request_id=service_request_item.id
                    task_space=EUAO.models.euao_service_space.objects.get(name='ControlAIX')
                    if operation_name=='poweron':
                        function=EUAO.models.euao_service_function.objects.get(name='StartVIOClient')
                    elif operation_name=='poweroff':
                        function=EUAO.models.euao_service_function.objects.get(name='ShutdownVIOClient')
                    elif operation_name=='reset':
                        function=EUAO.models.euao_service_function.objects.get(name='RestartVIOClient')
                    
                    est_exec_time=kwargs.get('est_exec_time',None)
                    plan_execute_time=kwargs.get('plan_execute_time',None)
                    
                    m_aix_server=vioclient_item.server
                    m_hmc=m_aix_server.hmc_server
                    
                    HMC_IP=m_hmc.ip
                    HMC_username=m_hmc.username
                    HMC_passwd=m_hmc.password
                    HMCServerName=m_aix_server.name
                    VIOClientName='%s_%s' % (vioclient_item.belong_to_username,vioclient_name)
                    HMC_ssh_port=aix_setting.hmc_default_port
                    HMC_cmd_prompt=m_hmc.prompt
                    profile_name='default'
                    
                    if operation_name=='poweron':
                        euao_task_parameter= """HMC_IP='%s',HMC_username='%s',HMC_passwd='%s',HMCServerName='%s',VIOClientName='%s',profile_name='%s',HMC_ssh_port='%s',HMC_cmd_prompt='%s'""" % (HMC_IP,HMC_username,HMC_passwd,HMCServerName,VIOClientName,profile_name,HMC_ssh_port,HMC_cmd_prompt)
                    else:
                        euao_task_parameter= """HMC_IP='%s',HMC_username='%s',HMC_passwd='%s',HMCServerName='%s',VIOClientName='%s',HMC_ssh_port='%s',HMC_cmd_prompt='%s'""" % (HMC_IP,HMC_username,HMC_passwd,HMCServerName,VIOClientName,HMC_ssh_port,HMC_cmd_prompt)
                    euao_task_status_created=EUAO.models.task_status.objects.get(name='created')
                    task_target_type=EUAO.models.target_type.objects.get(name='aix_vioclient')
                    target_instance_number=vioclient_item.id
                    euao_task=EUAO.models.task(service_request_id=service_request_id,\
                                            task_space=task_space,\
                                            function=function,\
                                            parameters=euao_task_parameter,\
                                            estimated_execute_time=est_exec_time,\
                                            plan_execute_time=plan_execute_time,\
                                            status=euao_task_status_created,\
                                            target_type=task_target_type,\
                                            target_instance_number=target_instance_number)
                
                    euao_task.save()
                                        
        else:
            pass
            
    except Exception,e:
        logger.error('Error in create euao task from service request: %s' % e)
        logger.debug(trace_back())
        request_error=workflow.models.RequestStatus.objects.get(request_status_id=13)
        service_request_item.request_status=request_error
        service_request_item.status_message=ServiceRequestStatusMessage['errorcreateeuao']
        service_request_item.save()
    

def reset_all():
    test_delete_approve()
    test_delete_service_request()
    test_delete_service_resource_alert()
    test_reset_user_aix_quota()

def ChangeServiceRequestStatus(service_request_id,request_status,delay_sec=0,**kwargs):
    if delay_sec>0:
        sleep(delay_sec)
    sr=workflow.models.ServiceRequest.objects.get(id=service_request_id)
    sr.request_status=request_status
    sr.save()

def passApprove(approve_item):
    setServiceRequestApprover(approve_item.id)
    sleep(3)
    sr=workflow.models.ServiceRequest.objects.get(id=approve_item.service_request_id)
    request_passapproval=workflow.models.RequestStatus.objects.get(request_status_id=4)
    sr.request_status=request_passapproval
    sr.save()
    """
    sleep(3)
    t=EThread(setServiceRequestApprover,(approve_item.id,))
    t.start()
    """
def setServiceRequestStatus(service_request_item,service_request_status,service_reqeust_status_message):
    sleep(3)
    service_request_item.request_status=service_request_status
    service_request_item.status_message=service_reqeust_status_message
    service_request_item.save()
    
    
def setServiceRequestApprover(approve_id):
    approve_item=workflow.models.Approve.objects.get(id=approve_id)
    logger.debug('Approve item: %s' % approve_item)
    if approve_item.approver:
        logger.debug('Approve item approver: %s' % approve_item.approver)
        sr=workflow.models.ServiceRequest.objects.get(id=approve_item.service_request_id)
        if sr.approver!=approve_item.approver:
            sr.approver=approve_item.approver
            sr.save()
   
def service_request_revoke_available(service_request_id):
    sr_item=workflow.models.ServiceRequest.objects.get(id=service_request_id)
    allow_request_status_id_list=[2,6,7,8,13]
    if sr_item.request_status.request_status_id in allow_request_status_id_list:
        return True
    else:
        return False

def revoke_service_request(service_request_id):
    try:
        sr_item=workflow.models.ServiceRequest.objects.get(id=service_request_id)
        revoke_status=workflow.models.RequestStatus.objects.get(request_status_id=14)
        sr_item.request_status=revoke_status
        sr_item.status_message=ServiceRequestStatusMessage['revoked']
        sr_item.save()
        return True
    except Exception,e:
        logger.error('Error in revoking service reqeust: %s' % service_request_id)
        logger.debug(trace_back())
        return False

def check_if_sysadmin(username):
    try:
        user=User.objects.get(username=username)
        
        for user_group_item in user.groups.all():
            if user_group_item.name==setting.sys_admin_group_name:
               return True
        return False
    except Exception,e:
                
        logger.error('Error in check user: %s' % username)
        logger.debug(trace_back())
        return False

def test_delete_service_request():
    srs=workflow.models.ServiceRequest.objects.all()
    for sr in srs:
        sr.delete()
def test_delete_service_resource_alert():
    sras=workflow.models.SystemResourceAlert.objects.all()
    for sra in sras:
        sra.delete()


def test_reset_user_aix_quota():
    for user_item in User.objects.all():
        for user_group_item in user_item.groups.all():
            if user_group_item.name==setting.aix_user_group_name:
                #reset user profile aix quota
                try:
                    user_profile=user_item.get_profile()
                    user_profile.aix_cpu_used=0
                    user_profile.aix_mem_used=0
                    user_profile.aix_count_used=0
                    user_profile.save()
                except Exception,e:
                    logger.debug('Error in reset %s \'s quota: %s' % (user_item.username,e))
                    logger.debug(trace_back())
            
def test_delete_approve():
    approves=workflow.models.Approve.objects.all()
    for a in approves:
        a.delete()
