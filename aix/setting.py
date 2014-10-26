# -*- coding: utf-8 -*-

vioclient_netcard={'manage_netcard':'en0','service_netcard':'en1'}
vioclient_virtual_eth_adapter='22/0/manage_ip_vlan_id///1,23/0/service_ip_vlan_id///1'
#vioclient_virtual_eth_adapter='22/0/35///1,23/0/98///1'

min_procs=1
max_procs=16

min_procs_unit=0.1
max_procs_unit=16.0

min_mem=1
max_mem=16

# for test init only
VIOServer1={'ip':'182.247.251.205',
            'username':'padmin',
            'password':'padmin',
            'prompt':'#',
            'version':'reserved'}

VIOServer2={'ip':'182.247.251.215',
            'username':'padmin',
            'password':'padmin',
            'prompt':'#',
            'version':'reserved'}

vioserver_default_port=23

NIMserver={'ip':'182.247.251.173',
           'username':'root',
           'password':'root',
           'prompt':'#',
           'version':'reserved'}

nimserver_default_port=23

HMC={'ip':'182.247.251.247',
    'username':'hscroot',
    'password':'abc1234',
    'prompt':'hscroot@localhost:~>',
    'version':'reserved'}



#list
AIX_Version=[{'version':'5307',
             'spot':'AIX5307spot',
             'lpp_source':'AIX5307standard',
             'mksysb':'AIX5307temp'},
             {'version':'6300',
             'spot':'AIX6300spot',
             'lpp_source':'AIX6300standard',
             'mksysb':'nimmmksysb'}]

vioclient_default_user='root'
vioclient_default_passwd='root'
vioclient_default_port=23
vioclient_default_cmd_prompt='#'
hmc_default_port=22

#list
#Do NOT change info below if you are not the cCloud Engineer.
###########################################################

vioclient_status=[
    {'status_id':0,
     'status':'ready to deploy'},
    {'status_id':1,
     'status':'deploying'},
    {'status_id':2,
     'status':'adjusting'},
    {'status_id':3,
     'status':'deleting'},
    {'status_id':4,
     'status':'deleted'},
    {'status_id':5,
     'status':'normal'},
    {'status_id':6,
     'status':'power off'},
    {'status_id':7,
     'status':'paused'},
    {'status_id':8,
     'status':'error in deploying'},
       ]

