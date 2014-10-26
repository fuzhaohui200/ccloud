import logging
logger=logging.getLogger('ecms')
#from vmware.models import vmware_os_type,vmware_template,vmware_vcenter,vmware_server,vmware_datastore_type,vmware_datastore,vmware_datacenter,vmware_machine_status,vmware_ip_status,vmware_manage_ip,vmware_service_ip,vmware_additional_ip,vmware_machine,vmware_resource_lock_status,vmware_resource_lock
import random
import vmware.models
import workflow.models
import EUAO.models
from django.contrib.auth.models import User
import datetime

import vmware.setting as setting

def FreezeVMwareLockedResource(**kwargs):
    esx=kwargs.get('esx')
    cpu=kwargs.get('cpu')
    mem=kwargs.get('mem')
    storage_type=kwargs.get('storage_type')
    data_store=kwargs.get('data_store')
    disk_space=kwargs.get('disk_space')
    manage_ip=kwargs.get('manage_ip')
    service_ip=kwargs.get('service_ip')
    
    if esx:
        logger.debug('Lock ESX')
        if cpu:
            #reduce available cpu in esx
            if esx.available_cpu>=cpu:
                esx.available_cpu-=cpu
            else:
                logger.error('Not enough cpu in esx: %s' % esx)
                return False
        if mem:
            if esx.available_mem_gb>=mem:
                esx.available_mem_gb-=mem
            else:
                logger.error('Not enough mem in esx: %s' % esx)
                return False
    if storage_type:
        logger.debug('Lock storage')
        if storage_type.type=='internal':
            if esx and disk_space:
                if esx.available_storage_capacity_gb>=disk_space:
                    esx.available_storage_capacity_gb-=disk_space
                else:
                    logger.error('Not enough space in esx: %s' % esx)
                    return False
            else:
                logger.debug('No esx or disk_space info')
            
            
            if data_store and disk_space:
                data_store.available_capacity_gb-=disk_space
                if data_store.available_capacity_gb>0:
                    pass
                    #data_store.save()
                else:
                    logger.error('DataStore %s does not have enough disk space.' % data_store)
                    return False
            else:
                logger.error('No data store or disk_space info')
                return False            
        elif storage_type.type=='external':
            if data_store and disk_space:
                data_store.available_capacity_gb-=disk_space
                if data_store.available_capacity_gb>0:
                    pass
                    #data_store.save()
                else:
                    logger.error('DataStore %s does not have enough disk space.' % data_store)
                    return False
            else:
                logger.error('No data store or disk_space info')
                return False
        else:
            logger.error('storage_type: %s not supported' % storage_type)
            return False
    
    if cpu or mem or disk_space:
        if esx.available_mem_gb>0 and esx.available_cpu>0:
            pass
            #esx.save()
        else:
            logger.error('esx: %s does not have enough resource.' % esx)
            return False
    
    if manage_ip:
        if manage_ip.status.status=='available':
            # set to lock status
            manage_ip.lock()
        else:
            logger.error('Manage ip : %s not available to lock.' % manage_ip)
            return False
    if service_ip:
        if service_ip.status.status=='available':
            #set to lock status
            service_ip.lock()
        else:
            logger.error('Service ip : %s not available to lock.' % service_ip)
            return False
    if esx:
        esx.save()
    if data_store:
        data_store.save()
    
    if manage_ip:
        manage_ip.save()
    if service_ip:
        service_ip.save()
    
    return True
    
def CalulateVMmachinePrice(cpu,mem,hdd_size_gb,esx,datastore):
    return 100

#create vmware_machine from vmware_resource_lock and ServiceRequest
def CreateVMware_machine(resource_locked_item,service_request):
    #check resource_lock available
    """
    {'name':'test_leon','type':'vmware_machine','cpu':2,'mem':4,'os_type':'Linux-suse11sp1','vmware_machine_store_type':'internal'}
    """
    
    latest_service_request_id=resource_locked_item.service_request_id
    request_parameter_dict=eval(service_request.request_parameter)
    
    name=request_parameter_dict.get('name')
    manage_ip=resource_locked_item.vmware_manage_ip
    service_ip=resource_locked_item.vmware_service_ip
    additional_ip=None
    dns_ip_1=setting.dns1
    dns_ip_2=setting.dsn2
    
    username=service_request.submitter
    m_user=User.objects.get(username=username)
    user_profile=m_user.get_profile()
    user_branch_bank=user_profile.branch_bank
    user_department=user_profile.department
    user_project_group=user_profile.project_group
    
    os_type_str=request_parameter_dict.get('os_type')
    
    if os_type_str.upper().find('LINUX')>=0:
        manage_username=setting.linux_default_username
        manage_password=setting.linux_default_passwd
    else:
        manage_username=setting.windows_defaut_username
        manage_password=setting.windows_default_passwd
        
    cpu_count=resource_locked_item.cpu
    memory_size_gb=resource_locked_item.mem
    hdd_size_gb=resource_locked_item.disk_space
    os=vmware.models.vmware_os_type.objects.get(os_concat__iexact=os_type_str)
    os_template=vmware.models.vmware_template.objects.get(os_type=os)
    esx=resource_locked_item.esx
    vcenter=esx.vcenter
    datastore=resource_locked_item.data_store
    
    workgroup=setting.workgroup
    
    start_date=datetime.date.today()
    end_date=None
    
    price_per_day=CalulateVMmachinePrice(cpu_count,memory_size_gb,hdd_size_gb,esx,datastore)
    expenses=0
    
    vm_status_ready_to_deploy=vmware.models.vmware_machine_status.objects.get(status_id=0)
    
    vm=vmware.models.vmware_machine(latest_service_request_id=latest_service_request_id,
                      name=name,
                      os_template=os_template,
                      manage_ip=manage_ip,
                      service_ip=service_ip,
                      additional_ip=additional_ip,
                      dns_ip_1=dns_ip_1,
                      dns_ip_2=dns_ip_2,
                      user=username,
                      user_branch_bank=user_branch_bank,
                      user_department=user_department,
                      user_project_group=user_project_group,
                      manage_username=manage_username,
                      manage_password=manage_password,
                      cpu_count=cpu_count,
                      memory_size_gb=memory_size_gb,
                      hdd_size_gb=hdd_size_gb,
                      os=os,
                      esx=esx,
                      vcenter=vcenter,
                      datastore=datastore,
                      workgroup=workgroup,
                      start_date=start_date,
                      end_date=end_date,
                      price_per_day=price_per_day,
                      expenses=expenses,
                      status=vm_status_ready_to_deploy)
    vm.save()
        
def CreateEUAOTask(vmware_machine_item,*args,**kwargs):
    service_request_id=vmware_machine_item.latest_service_request_id
    service_requtest_item=workflow.models.ServiceRequest.objects.get(id=service_request_id)
    request_parameter=eval(service_requtest_item.request_parameter)
    
    resource_type=request_parameter.get('type')
    if resource_type=='vmware_machine':
        space=EUAO.models.euao_service_space.objects.get(name='ControlVMware')
        function=EUAO.models.euao_service_function.objects.get(name='VMClone')
        est_exec_time=kwargs.get('est_exec_time',None)
        plan_execute_time=kwargs.get('plan_execute_time',None)
        status=EUAO.models.task_status.objects.get(name='created')
        vCenterUrl=vmware_machine_item.vcenter.webservice_url
        vCenterUsername=vmware_machine_item.vcenter.username
        vCenterPasswd=vmware_machine_item.vcenter.password
        NewVMName=vmware_machine_item.name
        
        #for test default, datacenter is only one
        DataCenterName=setting.datacentername
        
        vmTemplatePath=vmware_machine_item.os_template.path
        vmTemplatePasswd=vmware_machine_item.os_template.password
        NewVMPasswd=vmTemplatePasswd
        NewVMComputerName=''.join(random.choice('ABCDEFGHIJKLMOPQRSTUVWXYZ') for x in range(8))
        DNSServer1=vmware_machine_item.dns_ip_1
        NewVMIP=vmware_machine_item.manage_ip.ip
        NewVMGateway=vmware_machine_item.manage_ip.gateway
        NewVMMemory_MB=vmware_machine_item.memory_size_gb*1024
        NewVMCPU=vmware_machine_item.cpu_count
        ESXHostName=vmware_machine_item.esx.name
        DataStoreName=vmware_machine_item.datastore.name
        OS_Type=vmware_machine_item.os_template.os_type.os_type
        WorkGroup=setting.workgroup
        FullName=vmware_machine_item.name
        OrganizationName=setting.VMOrganizationName
        WindowsKey=setting.windows2003enterprise_key
        DNSServer2=vmware_machine_item.dns_ip_2
        OptionFromConfigFile=False
        

        euao_task_parameter="""vCenterUrl='%s',vCenterUsername='%s',vCenterPasswd='%s',NewVMName='%s',DataCenterName='%s',vmTemplatePath='%s',vmTemplatePasswd='%s',NewVMPasswd='%s',NewVMComputerName='%s',DNSServer1='%s',NewVMIP='%s',NewVMGateway='%s',NewVMMemory_MB='%s',NewVMCPU='%s',ESXHostName='%s',DataStoreName='%s',OS_Type='%s',WorkGroup='%s',FullName='%s',OrganizationName='%s',WindowsKey='%s',DNSServer2='%s',OptionFromConfigFile='%s'""" % (vCenterUrl,vCenterUsername, vCenterPasswd, NewVMName, DataCenterName, vmTemplatePath, vmTemplatePasswd, NewVMPasswd, NewVMComputerName, DNSServer1, NewVMIP, NewVMGateway, NewVMMemory_MB, NewVMCPU, ESXHostName, DataStoreName, OS_Type, WorkGroup, FullName, OrganizationName, WindowsKey, DNSServer2, OptionFromConfigFile)
        
        euao_task_status_created=EUAO.models.task_status.objects.get(name='created')
        
        euao_task=EUAO.models.task(service_request_id=service_request_id,\
                       task_space=space,\
                       function=function,\
                       parameters=euao_task_parameter,\
                       estimated_execute_time=est_exec_time,\
                       plan_execute_time=plan_execute_time,\
                       status=euao_task_status_created)
        euao_task.save()
        
        

#
#######################
# for test 
#######################
def test_reset_all():
    test_reset_ip_to_available()
    test_set_esx_to_default()
    test_delete_all_vm()
    test_delete_all_vm_lock_resource()
    
def test_reset_ip_to_available():
    ip_available=vmware.models.vmware_ip_status.objects.get(status_id=0)
    manage_ips=vmware.models.vmware_manage_ip.objects.all()
    for ip in manage_ips:
        ip.status=ip_available
        ip.save()
    
    service_ips=vmware.models.vmware_service_ip.objects.all()
    for ip in service_ips:
        ip.status=ip_available
        ip.save()

def test_set_esx_to_default():
    esxs=vmware.models.vmware_server.objects.all()
    for esx in esxs:
        esx.available_cpu=esx.total_cpu
        esx.available_mem_gb=esx.total_mem_gb
        esx.available_storage_capacity_gb=esx.total_storage_capacity_gb
        esx.save()

def test_delete_all_vm():
    vms=vmware.models.vmware_machine.objects.all()
    for vm in vms:
        vm.delete()

def test_delete_all_vm_lock_resource():
    vmlocks=vmware.models.vmware_resource_lock.objects.all()
    for vml in vmlocks:
        vml.delete()
