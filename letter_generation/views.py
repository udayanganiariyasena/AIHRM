from django.core.paginator import Paginator
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import DocumentRequest
from .view_functions.generate_document import send_document_email


@login_required
def document_requests_list(request):
    """View to list document requests with filtering and pagination."""

    # Get filter parameters
    doc_type = request.GET.get('doc_type', '')
    status = request.GET.get('status', '')

    # Filter document requests
    if request.user.is_superuser:
        document_requests = DocumentRequest.objects.all()
    else:
        document_requests = DocumentRequest.objects.filter(user=request.user)

    if doc_type:
        document_requests = document_requests.filter(document_type=doc_type)
    if status:
        document_requests = document_requests.filter(status=status)

    # Paginate results (10 per page)
    paginator = Paginator(document_requests, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Unique document types and statuses for filters
    doc_types = DocumentRequest.objects.values_list('document_type', flat=True).distinct()
    statuses = DocumentRequest.objects.values_list('status', flat=True).distinct()

    context = {
        'page_obj': page_obj,
        'doc_types': doc_types,
        'statuses': statuses
    }
    return render(request, 'listing.html', context)


@login_required
def edit_document_request(request, request_id):
    """View to edit a specific document request."""
    document_request = get_object_or_404(DocumentRequest, id=request_id)

    if request.method == "POST":
        if request.POST.get('status_dup') is not None:
            document_request.status = request.POST.get('status_dup')
            document_request.save()

            if document_request.status == 'Approved':
                if document_request.sent_status == 0:
                    send_document_email(document_request)

            return redirect('document_index')

        document_request.status = request.POST.get('status')
        document_request.document_type = request.POST.get('document_type')
        document_request.reason = request.POST.get('reason')
        document_request.save()

        return redirect('document_index')


    return render(request, 'edit_request.html', {'document_request': document_request})


@login_required
def delete_document_request(request, request_id):
    """View to delete a document request (admin-only)."""
    if not request.user.is_superuser:
        return redirect('document_index')

    document_request = get_object_or_404(DocumentRequest, id=request_id)
    document_request.delete()
    return redirect('document_index')

@login_required
def request_letter(request):
    if request.method == "POST":
        document_type = request.POST.get("document_type")
        reason = request.POST.get("reason")

        if not document_type or not reason:
            messages.error(request, "All fields are required.")
            return redirect("request_letter")

        DocumentRequest.objects.create(user=request.user, document_type=document_type, reason=reason)
        messages.success(request, "Your document request has been submitted successfully!")
        return redirect("document_index")

    return render(request, "request.html")
