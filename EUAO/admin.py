from django.contrib import admin

from EUAO.models import euao_service_function
from EUAO.models import euao_service_space
from EUAO.models import task
from EUAO.models import task_status
from EUAO.models import check_task
from EUAO.models import target_type

admin.site.register(euao_service_function)
admin.site.register(euao_service_space)
admin.site.register(task)
admin.site.register(task_status)
admin.site.register(check_task)
admin.site.register(target_type)