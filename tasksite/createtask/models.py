from django.db import models

# Create your models here.
from django.contrib.auth.models import User
import uuid
from .permissions  import Task

class UserTaskPermissions(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    is_owner = models.BooleanField(default=False)
    can_edit = models.BooleanField(default=False)
    can_delete = models.BooleanField(default=False)




