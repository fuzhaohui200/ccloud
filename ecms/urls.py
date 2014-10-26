#from django.conf.urls import patterns, include, url

import django
if float("%d.%d"%(django.VERSION[0],django.VERSION[1])) <= 1.5:
    from django.conf.urls.defaults import *
else:    
    from django.conf.urls import *
    
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

admin.autodiscover()
# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

from workflow.api import ServiceRequestByUserResource
from workflow.api import RequestStatusResource  
from workflow.api import RequestTypeResource

from workflow.api import ApproveResource
from workflow.api import ApproveStatusResource
from workflow.api import SystemAlertStatusResource
from workflow.api import SystemAlertResource

from aix.api import aix_violcient_resource
from aix.api import aix_service_ip
from aix.api import aix_version_resource
from aix.api import aix_vioclient_status_resource
from aix.api import aix_hdisk_type_resource
from aix.api import aix_vioclient_type_resource
from aix.api import aix_vlan_resource

from UI.api import NoticeResource
from charge.api import vioclient_usage_log_resource

from django.views.generic import RedirectView

#APScheduler add job
from charge.charge_function import add_to_sche
add_to_sche()

# rest api
ui_notice_resource=NoticeResource()
request_type_resource=RequestTypeResource()
request_status_resource=RequestStatusResource()
service_request_by_user_resource=ServiceRequestByUserResource()

approve_status_resource=ApproveStatusResource()
approve_resource=ApproveResource()
system_alert_resource=SystemAlertResource()
system_alert_status_resource=SystemAlertStatusResource()

vioclient_resource=aix_violcient_resource()
service_ip=aix_service_ip()
aix_version=aix_version_resource()
aix_vioclient_status=aix_vioclient_status_resource()
vioclient_usage_log_query=vioclient_usage_log_resource()

vioclient_type=aix_vioclient_type_resource()
vlan=aix_vlan_resource()
hdisk_type=aix_hdisk_type_resource()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'ecms.views.home', name='home'),
    # url(r'^ecms/', include('ecms.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),
    (r'^admin/',include(admin.site.urls)),
)

"""
from django.conf import settings

if settings.DEBUG is False:
    urlpatterns += patterns('', url(r'^static/(?P .*)$', 'django.views.static.serve', { 'document_root': settings.STATIC_ROOT, }), )
"""

sys_reset_init_urlpatterns=patterns('ecms.view',
    #for test, rest all resource and clear all request, approve, alert
    ('^clear_all/$','clear_all'),
    ('^clear_aix/$','clear_aix'),
    ('^clear_euao/$','clear_euao'),
    #('^clear_vmware/$','clear_vmware'),
    ('^clear_workflow/$','clear_workflow'),
    ('^init_all/$','init_all'),
    ('^init_aix/$','init_aix'),
    ('^init_test_aix/$','init_test_aix_data'),
    ('^init_delete_test_aix/$','init_delete_aix_test'),
    ('^add_aix_service_ip/$','add_aix_service_ip'),
    ('^add_aix_manage_ip/$','add_aix_manage_ip'),
    ('^add_aix_ip_from_resource_pool/$','add_ip_from_cfg'),
    ('^add_aix_hdisk_from_resource_pool/$','add_hdisk_from_cfg')
)


urlpatterns+=sys_reset_init_urlpatterns

tastypie_api_urlpatterns=patterns('',
    (r'^api/',include(request_status_resource.urls)),
    (r'^api/',include(request_type_resource.urls)),
    (r'^api/',include(service_request_by_user_resource.urls)),
    (r'^api/',include(approve_resource.urls)),
    (r'^api/',include(approve_status_resource.urls)),
    (r'^api/',include(system_alert_resource.urls)),
    (r'^api/',include(system_alert_status_resource.urls)),
    (r'^api/',include(vioclient_resource.urls)),
    (r'^api/',include(service_ip.urls)),
    (r'^api/',include(aix_version.urls)),
    (r'^api/',include(aix_vioclient_status.urls)),
    (r'^api/',include(ui_notice_resource.urls)),
    (r'^api/',include(vioclient_usage_log_query.urls)),
    (r'^api/',include(vlan.urls)),
    (r'^api/',include(hdisk_type.urls)),
    (r'^api/',include(vioclient_type.urls)),
)

redirect_url=('',
              ('/api/service_request_by_user/?format=json&take=(?p<a>\d+)&skip=(?p<b>\d+)&page=(?p<c>\d+)&pageSize=(?p<d>\d+)', RedirectView.as_view(url='^/api/service_request_by_user/?offset=%(b)s&limit=%(a)s&format=json')),
              ('^/$', RedirectView.as_view(url='^/index/$')),
)

urlpatterns+=tastypie_api_urlpatterns

urlpatterns+=staticfiles_urlpatterns()

html_template_patterns=patterns('UI.views',
    ('^$','index'),
    ('^index/$','index'),
    ('^functionContent/$','functionContent'),
    ('^overview/$','overview'),
    ('^useTerms/$','useTerms'),
    ('^privicyStatement/$','privicyStatement'),
    ('^aboutMe/$','aboutMe'),
    ('^change_passwd_page/$','change_passwd_page'),
    ('^login/$','user_login'),
    ('^logout/$','user_logout'),
)

ajax_patterns=patterns('UI.views',
    ('^user_auth/$','user_auth'),
    ('^get_user_groups/$','get_user_groups'),
    ('^get_username/$','get_username'),
    ('^change_passwd/$','change_passwd'),
    ('^vioclient_operate_available/$','vioclient_operate_available'),
    ('^get_user_aix_quota/$','get_user_aix_quota'),
    ('^service_request_revoke_available/$','servicerequest_revoke_available'),
    ('^revoke_service_request/$','revoke_service_request'),
)


for_test_only_patterns=patterns('UI.views',
    ('^read_euao_log/$','read_euao_log'),
    ('^read_ecms_log/$','read_ecms_log'),
)


urlpatterns+=html_template_patterns
urlpatterns+=ajax_patterns
urlpatterns+=for_test_only_patterns
