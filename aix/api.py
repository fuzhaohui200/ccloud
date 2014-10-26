import logging
logger=logging.getLogger('ecms')
from django.contrib.auth.models import User

from tastypie.resources import ModelResource
from tastypie import fields, utils
from tastypie.resources import ALL
from tastypie.resources import ALL_WITH_RELATIONS
from tastypie.serializers import Serializer
from tastypie.authentication import BasicAuthentication
from tastypie.authentication import MultiAuthentication
from tastypie.authorization import DjangoAuthorization
from tastypie.authorization import Authorization

from aix.api_authorization import aix_user_Authentication
from aix.api_authorization import CurrentUserVIOClientAuthorization

from aix.models import vioclient
from aix.models import aix_service_ip
from aix.models import vioclient_status
from aix.models import aix_version

from aix.models import hdisk_type
from aix.models import vlan
from aix.models import vlan_type
from aix.models import vioclient_type

class aix_hdisk_type_resource(ModelResource):
    class Meta:
        list_allowed_methods=['get']
        queryset=hdisk_type.objects.all()
        resource_name='aix_hdisk_type'
        
        authentication=MultiAuthentication(aix_user_Authentication())
        authorization=DjangoAuthorization()

class aix_vlan_type_resource(ModelResource):
    class Meta:
        list_allowed_methods=['get']
        queryset=vlan_type.objects.all()
        filtering={
            'id':('exact',)
        }
        resource_name='aix_vlan_type'

        authentication=MultiAuthentication(aix_user_Authentication())
        authorization=DjangoAuthorization()

class aix_vlan_resource(ModelResource):
    type=fields.ToOneField(aix_vlan_type_resource,'type',full=True)
    class Meta:
        list_allowed_methods=['get']
        queryset=vlan.objects.all()
        filtering={
            'type':ALL_WITH_RELATIONS,
        }
        resource_name='aix_vlan'

        authentication=MultiAuthentication(aix_user_Authentication())
        authorization=DjangoAuthorization()
        
class aix_vioclient_type_resource(ModelResource):
    class Meta:
        list_allowed_methods=['get']
        queryset=vioclient_type.objects.all()
        resource_name='aix_vioclient_type'

        authentication=MultiAuthentication(aix_user_Authentication())
        authorization=DjangoAuthorization()
        
class aix_service_ip(ModelResource):
    class Meta:
        list_allowed_methods=['get']
        queryset=aix_service_ip.objects.all()
        excludes=['id','netmask','gateway','status']
        resource_name='service_ip'
        
class aix_version_resource(ModelResource):
    class Meta:
        list_allowed_methods=['get']
        queryset=aix_version.objects.all()
        excludes=['lpp_source','mksysb','spot']
        resource_name='aix_version'

class aix_vioclient_status_resource(ModelResource):
    class Meta:
        list_allowed_methods=['get']
        queryset=vioclient_status.objects.all()
        excludes=['status_id']
        resource_name='aix_vioclient_status'

class aix_violcient_resource(ModelResource):
    service_ip=fields.ToOneField(aix_service_ip,'service_ip',full=True)
    status=fields.ToOneField(aix_vioclient_status_resource,'status',full=True)
    class Meta:
        
        list_allowed_methods=['get']
        queryset=vioclient.objects.all()
        
        excludes=['desired_procs_unit','latest_service_request_id','manage_netcard','max_mem','max_procs','max_procs_unit','min_mem','min_procs','min_procs_unit','password','resource_uri','service_netcard','username','virtual_eth_adapters','virtual_scsi_adapter']
        
        filtering={
            'belong_to_username': ('exact',)
        }
        resource_name='vioclient'
        authentication=MultiAuthentication(CurrentUserVIOClientAuthorization())
        authorization=DjangoAuthorization()