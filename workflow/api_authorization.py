from tastypie.authentication import Authentication
from tastypie.authorization import Authorization
import workflow.setting as setting
from models import ServiceRequest

import logging
logger=logging.getLogger('ecms')

class vmware_user_Authentication(Authentication):
    def is_authenticated(self, request, **kwargs):
        if request.user:
            try:
                for group_item in request.user.groups.all():
                    if group_item.name==setting.vmware_user_group_name:
                        return True
                return False
            except Exception,e:
                logger.error('Authentication error. %s' % e)
                return False
        return False

    # Optional but recommended
    def get_identifier(self, request):
        return request.user.username
    
    """
    def apply_limits(self, request, object_list):
        if request and hasattr(request, 'user'):
            return object_list.filter(ServiceRequest__submitter=request.user.username)
        return object_list.none()
    """
    

class aix_user_Authentication(Authentication):
    def is_authenticated(self, request, **kwargs):
        if request.user:
            try:
                for group_item in request.user.groups.all():
                    if group_item.name==setting.aix_user_group_name:
                        return True
                return False
            except Exception,e:
                logger.error('Authentication error. %s' % e)
                return False
        return False

    # Optional but recommended
    def get_identifier(self, request):
        return request.user.username
    
class common_admin_authentication(Authentication):
    
    def is_authenticated(self, request, **kwargs):
        if request.user:
            try:
                for group_item in request.user.groups.all():               
                    if group_item.name==setting.common_admin_group_name:
                        return True
                return False
            except Exception,e:
                logger.error('Authentication error. %s' % e)
                return False                
        return False

    # Optional but recommended
    def get_identifier(self, request):
        return request.user.username
    
class sys_admin_authentication(Authentication):
    def is_authenticated(self, request, **kwargs):
        if request.user:
            try:
                for group_item in request.user.groups.all():
                    if group_item.name==setting.sys_admin_group_name:
                        return True
                return False
            except Exception,e:
                logger.error('Authentication error. %s' % e)
                return False
        return False

    # Optional but recommended
    def get_identifier(self, request):
        return request.user.username


class user_admin_authentication(Authentication):
    def is_authenticated(self, request, **kwargs):
        if request.user:
            try:
                for group_item in request.user.groups.all():               
                    if group_item.name==setting.user_admin_group_name:
                        return True
                return False
            except Exception,e:
                logger.error('Authentication error. %s' % e)
                return False
        return False

    # Optional but recommended
    def get_identifier(self, request):
        return request.user.username

class CurrentUserServiceRequetsAuthorization(Authorization):
    #auto filter by currently login username in field: submitter
    def is_authenticated(self, request, object=None):
        if request.user:
            try:
                for group_item in request.user.groups.all():
                    if group_item.name==setting.vmware_user_group_name:
                        return True
            except Exception,e:
                logger.error('Authentication error. %s' % e)
                return False
        return False
       
    # Optional but useful for advanced limiting, such as per user.
    def apply_limits(self, request, object_list):
        if request and hasattr(request, 'user'):
            return object_list.filter(submitter=request.user.username)

        return object_list.none()