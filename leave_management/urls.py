from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

from leave_management.views import apply_leave, list_leave_requests, edit_leave_request, delete_leave_request

urlpatterns = [
    path('apply', apply_leave, name='apply_leave'),
    path('leave-requests/', list_leave_requests, name='leave_requests_list'),

    path('leaves/edit/<int:leave_id>/', edit_leave_request, name='edit_leave_request'),
    path('leaves/delete/<int:leave_id>/', delete_leave_request, name='delete_leave_request'),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)