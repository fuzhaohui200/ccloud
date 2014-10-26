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

from charge.models import vioclient_usage_log

from workflow.api_authorization import CurrentUserServiceRequetsAuthorization
from workflow.api_authorization import vmware_user_Authentication
from workflow.api_authorization import sys_admin_authentication
from workflow.api_authorization import common_admin_authentication
from workflow.api_authorization import user_admin_authentication
from workflow.api_authorization import aix_user_Authentication


class vioclient_usage_log_resource(ModelResource):
    class Meta:
        list_allowed_methods=['get']
        queryset=vioclient_usage_log.objects.all()
        resource_name='vioclient_usage_log'
        authentication=MultiAuthentication(sys_admin_authentication())
        authorization=DjangoAuthorization()
