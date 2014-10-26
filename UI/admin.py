from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User

from UI.models import Notice

admin.site.register(Notice)
