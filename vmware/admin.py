"""
from django.contrib import admin
from vmware.models import vmware_datacenter
from vmware.models import vmware_datastore
from vmware.models import vmware_datastore_type
from vmware.models import vmware_machine
from vmware.models import vmware_os_type
from vmware.models import vmware_server
from vmware.models import vmware_template
from vmware.models import vmware_vcenter
from vmware.models import vmware_machine_status
from vmware.models import vmware_manage_ip
from vmware.models import vmware_service_ip
from vmware.models import vmware_ip_status
from vmware.models import vmware_resource_lock
from vmware.models import vmware_resource_lock_status
from vmware.models import vmware_additional_ip

admin.site.register(vmware_datacenter)
admin.site.register(vmware_datastore)
admin.site.register(vmware_datastore_type)
admin.site.register(vmware_machine)
admin.site.register(vmware_os_type)
admin.site.register(vmware_server)
admin.site.register(vmware_template)
admin.site.register(vmware_vcenter)
admin.site.register(vmware_machine_status)
admin.site.register(vmware_manage_ip)
admin.site.register(vmware_service_ip)
admin.site.register(vmware_ip_status)
admin.site.register(vmware_resource_lock)
admin.site.register(vmware_resource_lock_status)
admin.site.register(vmware_additional_ip)
"""