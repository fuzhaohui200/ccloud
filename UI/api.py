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


from workflow.api_authorization import CurrentUserServiceRequetsAuthorization
from workflow.api_authorization import vmware_user_Authentication
from workflow.api_authorization import sys_admin_authentication
from workflow.api_authorization import common_admin_authentication
from workflow.api_authorization import user_admin_authentication
from workflow.api_authorization import aix_user_Authentication

from UI.models import Notice

class NoticeResource(ModelResource):
    class Meta:
        list_allowed_methods = ['get']
        queryset=Notice.objects.all()
        resource_name='NoticeResource'
        authentication=MultiAuthentication(aix_user_Authentication(),common_admin_authentication(),sys_admin_authentication())
        authorization=DjangoAuthorization()
