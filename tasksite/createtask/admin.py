from django.contrib import admin

# Register your models here.
from createtask.models import UserTaskPermissions
from createtask.permissions import Task

admin.site.register(Task)
admin.site.register(UserTaskPermissions)