
from django.contrib import admin
from django.urls import path, include
from createtask import views
from django.contrib.auth.views import LoginView
urlpatterns = [
   path('', views.dash, name='dashboard'),
   path('create/', views.create_task, name='create'),
   path('login/', LoginView.as_view(template_name='login.html'), name='login'),
   path('join/', views.join_task, name='join'),
   path('task/<str:code>/', views.task_detail, name='task_detail'),
   path('tasks/<str:code>/update/', views.update_task, name='update_task'),
    path('tasks/<str:code>/close/', views.close_task, name='close_task'),
    path('tasks/<str:code>/delete/', views.delete_task, name='delete_task'),
    path('list/', views.task_list, name='task_list'),
    path('tasks/<str:code>/invite_user/', (views.invite_user), name='invite_user'),
    path('tasks/<str:code>/remove_user/<int:user_id>/', (views.remove_user), name='remove_user'),
    path('tasks/<str:code>/set_permissions/<int:user_id>/', (views.set_permissions), name='set_permissions'),
    path('tasks/<str:code>/view_task_users/', (views.view_task_users), name='view_task_users'),

    
]