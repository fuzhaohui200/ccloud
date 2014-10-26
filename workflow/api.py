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

from workflow.models import ServiceRequest,RequestType,RequestStatus
from workflow.models import SystemResourceAlertStatus
from workflow.models import SystemResourceAlert
from workflow.models import Approve
from workflow.models import ApproveStatus

from workflow.api_authorization import CurrentUserServiceRequetsAuthorization
from workflow.api_authorization import vmware_user_Authentication
from workflow.api_authorization import sys_admin_authentication
from workflow.api_authorization import common_admin_authentication
from workflow.api_authorization import user_admin_authentication
from workflow.api_authorization import aix_user_Authentication



class RequestTypeResource(ModelResource):
    class Meta:
        list_allowed_methods = ['get']
        queryset=RequestType.objects.all()
        resource_name='RequestType'
        
        filtering={
            'request_type_id': ('exact','startswith',)
        }
        authentication=MultiAuthentication(common_admin_authentication(),sys_admin_authentication())
        authorization=DjangoAuthorization()

class RequestStatusResource(ModelResource):
    class Meta:
        list_allowed_methods = ['get']
        queryset=RequestStatus.objects.all()
        
        filtering={
            'request_status_id': ('lt','tg','exact','startswith',)
        }
        resource_name='RequestStatus'
        authentication=MultiAuthentication(aix_user_Authentication(),vmware_user_Authentication(),common_admin_authentication(),sys_admin_authentication())
        authorization=DjangoAuthorization()
        
class UserResource(ModelResource):
    class Meta:
        queryset = User.objects.all()
        resource_name = 'user'
        excludes = ['email', 'password', 'is_active', 'is_staff','is_superuser']
        allowed_methods = ['get']
        
        authentication=MultiAuthentication(aix_user_Authentication(),vmware_user_Authentication(),common_admin_authentication(),sys_admin_authentication())
        authorization=DjangoAuthorization()
        
class ServiceRequestByUserResource(ModelResource):
    request_type = fields.ToOneField(RequestTypeResource, 'request_type',full=True)
    request_status=fields.ToOneField(RequestStatusResource,'request_status',full=True)
    #user=fields.ForeignKey(UserResource,'user')
    class Meta:
        list_allowed_methods=['get','post','put']
        filtering={
            'request_status':ALL_WITH_RELATIONS,
        }
        queryset=ServiceRequest.objects.all()
        resource_name='service_request_by_user'
        excludes=['submitter','user']
        authentication=MultiAuthentication(aix_user_Authentication(),vmware_user_Authentication(),common_admin_authentication(),sys_admin_authentication())
        authorization=DjangoAuthorization()
        #authorization=CurrentUserServiceRequetsAuthorization()
        
    def obj_create(self, bundle, request=None, **kwargs):
        return super(ServiceRequestByUserResource, self).obj_create(bundle, request, user=request.user)

    def apply_authorization_limits(self, request, object_list):
        return object_list.filter(user=request.user).order_by('-id')
        
class ApproveStatusResource(ModelResource):
    class Meta:
        list_allowed_methods=['get']
        queryset=ApproveStatus.objects.all()
        filtering={
            'approve_status_id': ('exact','startswith',)
        }
        resource_name='ApproveStatus'
        #excludes=['approve_status_id']
        authentication=MultiAuthentication(common_admin_authentication(),sys_admin_authentication())
        authorization=DjangoAuthorization()

class ApproveResource(ModelResource):
    approve_status=fields.ToOneField(ApproveStatusResource,'approve_status',full=True)
    class Meta:
        list_allowed_methods=['get','put']
        filtering={
            'approve_status':ALL_WITH_RELATIONS,
        }
        queryset=Approve.objects.all()
        ordering=['-id']
        resource_name='approve'
        authentication=MultiAuthentication(common_admin_authentication(),sys_admin_authentication())
        authorization=DjangoAuthorization()
        
    def obj_update(self, bundle, request, **kwargs):
        bundle=super(ApproveResource,self).obj_update(bundle,request,**kwargs)
        bundle.obj.approver=request.user.username
        bundle.obj.save()
        return bundle

class SystemAlertStatusResource(ModelResource):
    
    class Meta:
        list_allowed_methods=['get']
        queryset=SystemResourceAlertStatus.objects.all()
        filtering={
            'status_id': ('exact','startswith',)
        }
        resource_name='system_alert_status'
        authentication=MultiAuthentication(sys_admin_authentication())
        authorization=DjangoAuthorization()

class SystemAlertResource(ModelResource):
    status=fields.ToOneField(SystemAlertStatusResource,'status',full=True)
    class Meta:
        list_allowed_methods=['get','put']
        
        filtering={
            'status':ALL_WITH_RELATIONS,
        }
        
        queryset=SystemResourceAlert.objects.all()
        resource_name='system_alert'
        authentication=MultiAuthentication(common_admin_authentication(),sys_admin_authentication())
        authorization=DjangoAuthorization()