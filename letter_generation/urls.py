from django.urls import path

from letter_generation.views import document_requests_list, request_letter, edit_document_request, \
    delete_document_request

urlpatterns = [
    path('index', document_requests_list, name='document_index'),
    path('request', request_letter, name='request_letter'),

    path('documents/edit/<int:request_id>/', edit_document_request, name='edit_document_request'),
    path('documents/delete/<int:request_id>/', delete_document_request, name='delete_document_request')

]