from django.contrib import admin
from models import aix_ip_status
from models import aix_manage_ip
from models import aix_server
from models import aix_service_ip
from models import aix_manage_ip
from models import hdisk
from models import hmc
from models import vioclient
from models import nim_server
from models import aix_version
from models import resource_available
from models import vioclient_status
from models import vio_server
from models import aix_resource_lock_status
from models import aix_resource_lock
from models import vhost
from models import vlan
from models import hdisk_type
from models import vioclient_type
from models import vlan_type


admin.site.register(aix_ip_status)
admin.site.register(aix_manage_ip)
admin.site.register(aix_server)
admin.site.register(aix_service_ip)
admin.site.register(hdisk)
admin.site.register(hmc)
admin.site.register(vioclient)
admin.site.register(nim_server)
admin.site.register(aix_version)
admin.site.register(resource_available)
admin.site.register(vioclient_status)
admin.site.register(vio_server)
admin.site.register(aix_resource_lock_status)
admin.site.register(aix_resource_lock)
admin.site.register(vhost)
admin.site.register(vlan)
admin.site.register(vlan_type)
admin.site.register(hdisk_type)
admin.site.register(vioclient_type)