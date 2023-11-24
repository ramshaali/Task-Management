from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render

from django.shortcuts import render, redirect
import uuid
from django.db.models import Q

from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User

from django.utils import timezone
from django.contrib import messages


from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from .models import UserTaskPermissions
from .permissions import Task



from django.utils.html import strip_tags

from random import choices
from string import ascii_uppercase, digits

from django.contrib.auth import get_user
def task_detail(request, code):
    task = get_object_or_404(Task, code=code)
    user_task_permissions = UserTaskPermissions.objects.filter(task=task)
    assigned_users = user_task_permissions
    return render(request, 'task_detail.html', {'task': task, 'assigned_users': assigned_users})
    

# Create your views here.


'''def create_task(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        due_date = request.POST.get('due_date')
        task = Task.objects.create(title=title, description=description, due_date=due_date,  created_date=timezone.now())
        return redirect('task_detail', code=task.code)
    return render(request, 'create_task.html')'''



def create_task(request):
    if request.method == 'POST':
        # Get data from the request object
        title = request.POST.get('title')
        description = request.POST.get('description')
        due_date = request.POST.get('due_date')

        # Generate a unique code for the task
        code = uuid.uuid4().hex[:6]

        # Create a new task object and save it to the database
        task = Task(title=title, description=description, due_date=due_date, code=code, owner=get_user(request),completed=False, completed_date=None)
        task.save()

        # Redirect the user to the task detail page
        return redirect('task_detail', code=task.code)
        #return render(request, 'task_detail.html', {'task': task})
    else:
        return render(request, 'createTask.html')



@login_required
def join_task(request):
    if request.method == 'POST':
        code = request.POST.get('code')
        try:
            task = Task.objects.get(code=code)
        except Task.DoesNotExist:
            task = None
        if task:
            # Create the UserTaskPermissions object for the current user
            task.assigned_users.add(request.user)
            task_user, created = UserTaskPermissions.objects.get_or_create(task=task, user=request.user, defaults={'can_edit': False})
            if created:
                messages.success(request, f"You've joined the task '{task.title}'")
            else:
                messages.warning(request, f"You're already a member of the task '{task.title}'")
            return redirect('task_detail', code=task.code)
        else:
            error_message = 'Invalid code. Please try again.'
    else:
        error_message = None

    return render(request, 'JoinTask.html', {'error_message': error_message})







@login_required
def update_task(request, code):
    task = get_object_or_404(Task, code=code)

    # permission or not
    if request.user == task.owner or UserTaskPermissions.objects.filter(user=request.user, task=task, can_edit=True).exists():
        if request.method == 'POST':
            # Get data
            task.title = request.POST.get('title')
            task.description = request.POST.get('description')
            task.due_date = request.POST.get('due_date')

            # Save data
            task.save()

            # Redirect
            return redirect('task_detail', code=task.code)

        return render(request, 'update_task.html', {'task': task})
    else:
        #  if no permission 
        return redirect('task_detail', code=task.code)



@login_required
def close_task(request, code):
    task = get_object_or_404(Task, code=code, owner=request.user)

    if request.method == 'POST':
        task.completed = True
        task.completed_date = timezone.now()
        task.save()
        return redirect('task_detail', code=task.code)

    return render(request, 'close_task.html', {'task': task})


@login_required
def delete_task(request, code):
    task = get_object_or_404(Task, code=code, owner=request.user)

    if request.method == 'POST':
        task.delete()
        return redirect('task_list')        

    return render(request, 'delete_task.html', {'task': task})

@login_required
def invite_user(request, code):
    task = get_object_or_404(Task, code=code, owner=request.user)
    if request.method == 'POST':
        email = request.POST['email']
        # Get or create the user object
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            user = None
        if not user:
            # Create a new user object if user does not exist
            # You can customize this part to your needs
            user = User.objects.create_user(username=email.split('@')[0], email=email, password=User.objects.make_random_password())
        # Create a UserTaskPermissions object for the user
        task_user, created = UserTaskPermissions.objects.get_or_create(task=task, user=user, defaults={'can_edit': True})
        if not created:
            messages.warning(request, f'User {email} is already a member of this task')
        else:
            # Add the user to the assigned users in the Task model
            task.assigned_users.add(user)
            # Generate a unique code for the invitation
            invitation_code = ''.join(choices(ascii_uppercase + digits, k=6))
            task_user.invitation_code = invitation_code
            task_user.save()

            # Send an email invitation to the user
            subject = f"You've been invited to collaborate on the task '{task.title}'"
            html_message = render_to_string('tasks/invite_user_email.html', {'task': task, 'invitation_code': invitation_code})
            plain_message = strip_tags(html_message)
            from_email = 'task_manager@example.com'
            recipient_list = [email]
            send_mail(subject, plain_message, from_email, recipient_list, html_message=html_message)

            messages.success(request, f'Invitation sent to {email}')
        return redirect('task_detail', code=code)
    else:
        return render(request, 'invite_user.html', {'task': task})



@login_required
def remove_user(request, code, user_id):
    task = get_object_or_404(Task, code=code, owner=request.user)
    user_task_permission = get_object_or_404(UserTaskPermissions, task=task, user=user_id)
    if request.method == 'POST':
        user_task_permission.delete()
        messages.success(request, 'User removed from task')
        return redirect('task_detail', code=code)
    else:
        return render(request, 'remove_user.html', {'task': task, 'user_task_permission': user_task_permission})

@login_required
def set_permissions(request, code, user_id):
    task = get_object_or_404(Task, code=code, owner=request.user)
    user_task_permission = get_object_or_404(UserTaskPermissions, task=task, user=user_id)
    if request.method == 'POST':
        user_task_permission.can_edit = request.POST.get('can_edit', False)
        user_task_permission.can_delete = request.POST.get('can_delete', False)
        user_task_permission.is_owner = request.POST.get('is_owner', False)
        user_task_permission.save()
        messages.success(request, 'Permissions updated')
        return redirect('task_detail', code=code)
    else:
        return render(request, 'set_permissions_user.html', {'task': task, 'user_task_permission': user_task_permission})

@login_required
def view_task_users(request, code):
    task = get_object_or_404(Task, code=code, owner=request.user)
    user_task_permissions = UserTaskPermissions.objects.filter(task=task)
    assigned_users = user_task_permissions
    return render(request, 'view_task_users.html', {'task': task, 'assigned_users': assigned_users})



@login_required
def task_list(request):
    tasks = Task.objects.filter(Q(owner=request.user) | Q(usertaskpermissions__user=request.user)).distinct()
 
    context = {
        'tasks': tasks,
    }
    return render(request, 'task_list.html', context)

@login_required
def dash(request):
    
    return render(request, 'dashboard.html')
