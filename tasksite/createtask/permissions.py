from django.db import models
from django.contrib.auth.models import User



'''class UserTaskPermissions(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    task = models.ForeignKey('Task', on_delete=models.CASCADE)
    is_owner = models.BooleanField(default=False)
    can_edit = models.BooleanField(default=False)
    can_delete = models.BooleanField(default=False)'''
class Task(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    due_date = models.DateField()
    created_date = models.DateTimeField(auto_now_add=True)
    code = models.CharField(max_length=6)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    completed = models.BooleanField(default=False)
    completed_date = models.DateTimeField(null=True, blank=True)
    assigned_users = models.ManyToManyField(User, related_name='assigned_tasks')