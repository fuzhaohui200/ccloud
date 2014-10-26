# -*- coding: utf-8 -*-
import aix.models
import aix.setting as setting
import workflow.models
import workflow.workflow_function
from ecms.EThread import EThread
import logging
logger=logging.getLogger('ecms')
import EUAO
from ecms.commonfunction import *


def FreezeAIXLockedResource(**kwargs):
    """
    usage:
            flag=FreezeLockedResource(aix_server=self.aix_server,
                                      cpu=self.cpu,
                                      mem=self.mem,
                                      service_ip=self.aix_service_ip,
                                      manage_ip=self.aix_manage_ip,
                                      hdisks=self.hdisks)
    """
    m_aix_server=kwargs.get('aix_server')
    m_cpu=kwargs.get('cpu')
    m_mem=kwargs.get('mem')
    m_service_ip=kwargs.get('service_ip')
    m_manage_ip=kwargs.get('manage_ip')
    
    # hdisks:   hdisk1,hdisk2,hdisk3....
    m_hdisks=kwargs.get('hdisks')
    m_vhost=kwargs.get('vhost')
    
    if m_aix_server:
        logger.debug('Lock AIX Server')
        if m_cpu:
            #reduce available cpu in esx
            if m_aix_server.available_cpu>=m_cpu:
                m_aix_server.available_cpu-=m_cpu
            else:
                logger.error('Not enough cpu in aix server: %s' % m_aix_server)
                return False
        if m_mem:
            if m_aix_server.available_mem>=m_mem:
                m_aix_server.available_mem-=m_mem
            else:
                logger.error('Not enough mem in aix server: %s' % m_aix_server)
                return False

    hdisk_instance_list=[]
    if m_vhost:
        logger.debug('Lock vhost: %s' % m_vhost)
        try:
            m_vhost.lock()
            
            if m_hdisks:
                logger.debug('Lock hdisk: %s' % m_hdisks)
                try:
                    m_hdisks_list=m_hdisks.split(',')
                    for hdisk_item in m_hdisks_list:
                        hdisk_instance=aix.models.hdisk.objects.get(rootvg_lun=hdisk_item)
                        hdisk_instance_list.append(hdisk_instance)
                        hdisk_instance.lock()
                        hdisk_instance.vhost=m_vhost
                        
                except Exception,e:
                    logger.error('Error in locking hdisk: %s' % m_hdisks)
                    logger.debug(trace_back())
                
        except Exception,e:
            logger.error('Error in locking vhost: %s' % m_vhost)
            logger.debug(trace_back())
    
    
    if m_manage_ip:
        if m_manage_ip.status.status=='available':
            # set to lock status
            m_manage_ip.lock()
        else:
            logger.error('Manage ip : %s not available to lock.' % m_manage_ip)
            return False
    if m_service_ip:
        if m_service_ip.status.status=='available':
            #set to lock status
            m_service_ip.lock()
        else:
            logger.error('Service ip : %s not available to lock.' % m_service_ip)
            return False
    if m_aix_server:
        m_aix_server.save()
    if len(hdisk_instance_list)>0:
        for hdisk_i in hdisk_instance_list:
            hdisk_i.save()
    if m_vhost:
        m_vhost.save()
    if m_manage_ip:
        m_manage_ip.save()
    if m_service_ip:
        m_service_ip.save()
    return True


################################
def CreateVIOClient(aix_resource_locked_item, service_request_item):
    belong_to_username=service_request_item.submitter
    latest_service_request_id=aix_resource_locked_item.service_request_id
    resource_lock_item=aix_resource_locked_item
    request_parameter_dict=eval(service_request_item.request_parameter)
    name=request_parameter_dict.get('name')
    server=aix_resource_locked_item.aix_server
    vioserver_1=server.vio_1
    vioserver_2=server.vio_2
    hdisks_str=aix_resource_locked_item.hdisk
    vhost=aix_resource_locked_item.vhost
    service_ip=aix_resource_locked_item.aix_service_ip
    manage_ip=aix_resource_locked_item.aix_manage_ip
    
    try:
        nim_server=aix.models.nim_server.objects.all()[0]
    except Exception,e:
        logger.error('At least one NIM Server is needed.')
        return
    os_version=aix.models.aix_version.objects.get(version=request_parameter_dict.get('os_type'))
    
    desired_procs=request_parameter_dict.get('cpu')
    desired_mem=request_parameter_dict.get('mem')
    
    vioclient_ready_status=aix.models.vioclient_status.objects.get(status_id=0)
    status=vioclient_ready_status
    
    m_vioclient=aix.models.vioclient()
    m_vioclient.belong_to_username=belong_to_username
    m_vioclient.latest_service_request_id=latest_service_request_id
    m_vioclient.resource_lock_item=resource_lock_item
    m_vioclient.name=name
    m_vioclient.server=server
    m_vioclient.vioserver_2=vioserver_2
    m_vioclient.vioserver_1=vioserver_1
    m_vioclient.hdisk=hdisks_str
    
    hdisks_list=hdisks_str.split(',')
    hdisk_number=1
    for item in hdisks_list:
        hdisk_instance=aix.models.hdisk.objects.get(rootvg_lun=item)
        if hdisk_number==1:
            hdisk_instance.vtd_name='%s_rootvg' % (name)
        else:
            hdisk_instance.vtd_name='%s_datavg%d' % (name,hdisk_number-1)
        hdisk_number+=1
        hdisk_instance.save()
    
    m_vioclient.vhost=vhost
    m_vioclient.service_ip=service_ip
    m_vioclient.manage_ip=manage_ip
    m_vioclient.virtual_eth_adapters=setting.vioclient_virtual_eth_adapter.replace('manage_ip_vlan_id',str(manage_ip.vlan.vlan_id)).replace('service_ip_vlan_id',str(service_ip.vlan.vlan_id))
    m_vioclient.nim_server=nim_server
    m_vioclient.os_version=os_version
    m_vioclient.desired_procs=desired_procs
    logger.debug('desired_procs: %s' % desired_procs)
    m_vioclient.desired_procs_unit=float(desired_procs)/10
    m_vioclient.desired_mem=desired_mem
    m_vioclient.status=status
    m_vioclient.save()

def CreateEUAOTask(vioclient_item,*args,**kwargs):
    service_request_id=vioclient_item.latest_service_request_id
    service_requtest_item=workflow.models.ServiceRequest.objects.get(id=service_request_id)
    request_parameter=eval(service_requtest_item.request_parameter)
    resource_type=request_parameter.get('type')
    if resource_type=='aix':
        space=EUAO.models.euao_service_space.objects.get(name='ControlAIX')
        function=EUAO.models.euao_service_function.objects.get(name='InstallWholeAIX')
        est_exec_time=kwargs.get('est_exec_time',None)
        plan_execute_time=kwargs.get('plan_execute_time',None)
        status=EUAO.models.task_status.objects.get(name='created')
        
        m_target_type=EUAO.models.target_type.objects.get(name='aix_vioclient')
        #m_target_pid=vioclient_item.id
        
        m_aix_server=vioclient_item.server
        m_hmc=m_aix_server.hmc_server
        m_vio_server_1=vioclient_item.vioserver_1
        m_vio_server_2=vioclient_item.vioserver_2
        
        m_vhost=vioclient_item.vhost
        m_hdisks=vioclient_item.hdisk
        
        
        m_nim=vioclient_item.nim_server
        m_os_version=vioclient_item.os_version
                
                
        HMC_IP=m_hmc.ip
        HMCServerName=m_aix_server.name
        
        #vioclient name in HMC: username_name
        VIOClientName='%s_%s' % (vioclient_item.belong_to_username,vioclient_item.name)
        
        min_mem=vioclient_item.min_mem*1024
        desired_mem=vioclient_item.desired_mem*1024
        max_mem=vioclient_item.max_mem*1024
        min_procs=vioclient_item.min_procs
        desired_procs=vioclient_item.desired_procs
        max_procs=vioclient_item.max_procs
        min_proc_units=vioclient_item.min_procs_unit
        desired_proc_units=vioclient_item.desired_procs_unit
        max_proc_units=vioclient_item.max_procs_unit
        virtual_eth_adapters=vioclient_item.virtual_eth_adapters
        virtual_scsi_adapter=m_vhost.virtual_scsi_adapter
        VIOServerIP_1=m_vio_server_1.ip
        VIOServerUsername_1=m_vio_server_1.username
        VIOServerPasswd_1=m_vio_server_1.password
        VIOServerIP_2=m_vio_server_2.ip
        VIOServerUsername_2=m_vio_server_2.username
        VIOServerPasswd_2=m_vio_server_2.password
        
        #rootvg_lun=m_hdisks.rootvg_lun
        """
        rootvg_lun_list_str and VTD_name_list_str are str seperated by ','
        like: 'hdisk1,hdisk2,hdisk3',
                'username_clientname_rootvg,
                username_clientname_datavg1,
                username_clientname_datavg2'
        """
        rootvg_lun_list_str=''
        VTD_name_list_str=''
        
        hdisk_list=m_hdisks.split(',')
        for hdisk_str in hdisk_list[:-1]:
            hdisk_item=aix.models.hdisk.objects.get(rootvg_lun=hdisk_str)
            rootvg_lun_list_str+=hdisk_item.rootvg_lun+','
            VTD_name_list_str+=hdisk_item.vtd_name+','
        hdisk_item=aix.models.hdisk.objects.get(rootvg_lun=hdisk_list[-1])
        rootvg_lun_list_str+=hdisk_item.rootvg_lun
        VTD_name_list_str+=hdisk_item.vtd_name
        
        vhost_name=m_vhost.vhost_name
        
        #VTD_name=m_hdisk.vtd_name
        
        
        NIM_IP=m_nim.ip
        NIM_username=m_nim.username
        NIM_passwd=m_nim.password
        ClientMgrIP=vioclient_item.manage_ip.ip
        
        #vlan
        VIOClientServiceIP_vlan=vioclient_item.service_ip.vlan.vlan_id
        VIOClientManageIP_vlan=vioclient_item.manage_ip.vlan.vlan_id
        
        #hostname, in NIM
        ServerHostName=vioclient_item.name
        
        spot=m_os_version.spot
        lpp_source=m_os_version.lpp_source
        mksysb=m_os_version.mksysb
        HMC_username=m_hmc.username
        HMC_passwd=m_hmc.password
        VIOClientMgrGateway=vioclient_item.manage_ip.gateway
        VIOClientServiceIP=vioclient_item.service_ip.ip
        VIOClientServiceGateway=vioclient_item.service_ip.gateway
        TargetServerUsername=vioclient_item.username
        TargetServerPasswd=vioclient_item.password
        TargetServerPort=setting.vioclient_default_port
        TargetServerCmdPrompt=setting.vioclient_default_cmd_prompt
        HMC_ssh_port=setting.hmc_default_port
        HMC_cmd_prompt=m_hmc.prompt
        VIOServerPort_1=setting.vioserver_default_port
        VIOCmd_prompt_1=m_vio_server_1.prompt
        VIOServerPort_2=setting.vioserver_default_port
        VIOCmd_prompt_2=m_vio_server_2.prompt
        NIM_port=setting.nimserver_default_port
        NIM_prompt=m_nim.prompt
                
                
                
        euao_task_parameter="""HMC_IP='%s',HMCServerName='%s',VIOClientName='%s',min_mem='%s',desired_mem='%s',max_mem='%s',min_procs='%s',desired_procs='%s',max_procs='%s',min_proc_units='%s',desired_proc_units='%s',max_proc_units='%s',virtual_eth_adapters='%s',virtual_scsi_adapter='%s',VIOServerIP_1='%s',VIOServerUsername_1='%s',VIOServerPasswd_1='%s',VIOServerIP_2='%s',VIOServerUsername_2='%s',VIOServerPasswd_2='%s',rootvg_lun='%s',vhost_name='%s',VTD_name='%s',NIM_IP='%s',NIM_username='%s',NIM_passwd='%s',ClientMgrIP='%s',ServerHostName='%s',spot='%s',lpp_source='%s',mksysb='%s',HMC_username='%s',HMC_passwd='%s',VIOClientMgrGateway='%s',VIOClientServiceIP='%s',VIOClientServiceGateway='%s',TargetServerUsername='%s',TargetServerPasswd='%s',TargetServerPort='%s',TargetServerCmdPrompt='%s',HMC_ssh_port='%s',HMC_cmd_prompt='%s',VIOServerPort_1='%s',VIOCmd_prompt_1='%s',VIOServerPort_2='%s',VIOCmd_prompt_2='%s',NIM_port='%s',NIM_prompt='%s',manage_ip_vlan='%s',service_ip_vlan='%s'""" % (HMC_IP,HMCServerName,VIOClientName,min_mem,desired_mem,max_mem,min_procs,desired_procs,max_procs,min_proc_units,desired_proc_units,max_proc_units,virtual_eth_adapters,virtual_scsi_adapter,VIOServerIP_1,VIOServerUsername_1,VIOServerPasswd_1,VIOServerIP_2,VIOServerUsername_2,VIOServerPasswd_2,rootvg_lun_list_str,vhost_name,VTD_name_list_str,NIM_IP,NIM_username,NIM_passwd,ClientMgrIP,ServerHostName,spot,lpp_source,mksysb,HMC_username,HMC_passwd,VIOClientMgrGateway,VIOClientServiceIP,VIOClientServiceGateway,TargetServerUsername,TargetServerPasswd,TargetServerPort,TargetServerCmdPrompt,HMC_ssh_port,HMC_cmd_prompt,VIOServerPort_1,VIOCmd_prompt_1,VIOServerPort_2,VIOCmd_prompt_2,NIM_port,NIM_prompt,VIOClientManageIP_vlan,VIOClientServiceIP_vlan)
        
        euao_task_status_created=EUAO.models.task_status.objects.get(name='created')
        euao_task=EUAO.models.task(service_request_id=service_request_id,\
                                    task_space=space,\
                                    function=function,\
                                    parameters=euao_task_parameter,\
                                    estimated_execute_time=est_exec_time,\
                                    plan_execute_time=plan_execute_time,\
                                    status=euao_task_status_created,\
                                    target_type=m_target_type,\
                                    target_instance_number=vioclient_item.id)
        
        
        
        
        euao_task.save()
        
        #create euao_check_task
        #function=EUAO.models.euao
        
        
def vioclient_operate_available(vioclient_name,operation_name):
    #check if vioclient_name can be issued operation_name
    #eg: if vioclient_name.status!=normal, and operation_name='poweroff', return true
    try:
        vioclient_item=aix.models.vioclient.objects.get(name=vioclient_name)
    except Exception,e:
        logger.error('No vioclient named %s' % vioclient_name)
        logger.debug(trace_back())
    vioclient_status_normal=aix.models.vioclient_status.objects.get(status_id=5)
    vioclient_status_poweroff=aix.models.vioclient_status.objects.get(status_id=6)
    
    try:
        if vioclient_item:
            if vioclient_item.status==vioclient_status_poweroff and operation_name=='recycle':
                return True
            elif vioclient_item.status==vioclient_status_poweroff and operation_name=='poweron':
                return True
            elif vioclient_item.status==vioclient_status_normal and operation_name=='poweroff':
                return True
            elif vioclient_item.status==vioclient_status_normal and operation_name=='reset':
                return True
            else:
                logger.debug('Operation: %s can not be performed on vioclient: %s' % (operation_name,vioclient_item))
                return False
        else:
            return False
    except Exception,e:
        logger.debug(trace_back())
        return False


def delayThreadChangeServiceRequestStatus(service_request_id,request_status,delay_sec=10):
    t=EThread(workflow.workflow_function.ChangeServiceRequestStatus,(service_request_id,request_status,delay_sec))
    t.start()