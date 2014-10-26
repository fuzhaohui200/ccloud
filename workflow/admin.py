from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User

from workflow.models import ApproveStatus
from workflow.models import Approve
from workflow.models import RequestStatus
from workflow.models import ServiceRequest
from workflow.models import RequestType

from workflow.models import SystemResourceAlertStatus
from workflow.models import SystemResourceAlert
#from workflow.models import View

from workflow.models import UserProfile
class UserProfileInline(admin.StackedInline):
    model=UserProfile
    can_delete=False
    verbose_name_plural='profile'

class UserAdmin(UserAdmin):
    inlines=(UserProfileInline, )
admin.site.unregister(User)
admin.site.register(User,UserAdmin)

admin.site.register(ApproveStatus)
admin.site.register(Approve)
admin.site.register(RequestStatus)
admin.site.register(RequestType)
admin.site.register(ServiceRequest)
admin.site.register(SystemResourceAlertStatus)
admin.site.register(SystemResourceAlert)
#admin.site.register(View)