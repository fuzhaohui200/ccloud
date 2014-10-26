from django.contrib import admin
from models import hdisk_pool
from models import vhost_pool
from models import aix_manage_ip_pool
from models import aix_service_ip_pool

admin.site.register(hdisk_pool)
admin.site.register(vhost_pool)
admin.site.register(aix_manage_ip_pool)
admin.site.register(aix_service_ip_pool)