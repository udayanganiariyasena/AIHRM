from django.urls import path

from staff_management.views import index

urlpatterns = [

    path('index', index, name='list_staff_members'),

]