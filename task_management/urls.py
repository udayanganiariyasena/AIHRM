from django.urls import path
from task_management.views import create_task, index, create_task_comment, edit_task, delete_task

urlpatterns = [

    path('create', create_task, name='create_task'),
    path('index', index , name='tasks_index'),
    path('create_task_comment', create_task_comment , name='create_comment'),

    path('task/edit/<int:task_id>/', edit_task, name='edit_task'),

    path('tasks/delete/<int:task_id>/', delete_task, name='delete_task'),

]