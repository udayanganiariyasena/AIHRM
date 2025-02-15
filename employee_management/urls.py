from django.urls import path
from employee_management.views import create, index, mark_attendance, attendance_list, edit_employee, edit_attendance, \
    delete_attendance

urlpatterns = [

    path('index', index, name='list_employees'),
    path('create', create, name='register_employee'),
    path("attendance/", mark_attendance, name="mark_attendance"),
    path('attendance-view/', attendance_list, name='attendance_list'),
    path('attendance/edit/<int:attendance_id>/', edit_attendance, name='edit_attendance'),
    path('attendance/delete/<int:attendance_id>/', delete_attendance, name='delete_attendance'),
    path('employee/edit/<int:employee_id>/', edit_employee, name='edit_employee'),

]