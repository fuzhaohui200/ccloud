# -*- coding: utf-8 -*-
# manage IP
aix_manage_ip_list='200.10.52.30-80'
aix_manage_ip_mask='255.255.255.0'
aix_manage_ip_gateway='200.10.52.100'

#service_IP
aix_service_ip_list='192.168.35.137-138'
aix_service_ip_mask='255.255.255.0'
aix_service_ip_gateway='192.168.35.254'


#hdisk
server1={'name':'Server-9117-MMA-SN062F860',
         'hdisk':'hdisk#2-10#',
         'vhost':'vhost#2-10#',
         'vtd_name':'vioc#2-10#_rootvg',
         'virtual_scsi_adapter':'#51-59#'
         }

server2={
    'name':'Server-9117-MMA-SN102CBB0',
    'hdisk':'hdisk#11-19#',
    'vhost':'vhost#11-19#',
    'vtd_name':'vioc#11-19#_rootvg',
    'virtual_scsi_adapter':'#61-69#',
}

hdisk=[server1,server2]
