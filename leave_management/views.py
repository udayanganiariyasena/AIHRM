from django.core.paginator import Paginator
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required

from employee_management.models import Employee
from home.drive_upload import save_file_in_local
from .models import LeaveRequest

@login_required
def apply_leave(request):
    if request.method == "POST":
        leave_type = request.POST.get("leave_type")
        start_date = request.POST.get("start_date")
        end_date = request.POST.get("end_date")
        reason = request.POST.get("reason")
        attachment = request.FILES.get("attachment")
        file_url = save_file_in_local(attachment)

        # Check required fields
        if not leave_type or not start_date or not end_date or not reason:
            messages.error(request, "All fields except attachment are required!")
            return redirect("apply_leave")

        # Save to database
        LeaveRequest.objects.create(
            user=request.user,
            leave_type=leave_type,
            start_date=start_date,
            end_date=end_date,
            reason=reason,
            attachment=file_url if file_url else ""
        )

        messages.success(request, "Your leave request has been submitted successfully!")
        return redirect("leave_requests_list")

    return render(request, "create.html")



@login_required
def list_leave_requests(request):
    # Retrieve filter parameters from the request
    leave_type = request.GET.get("leave_type")
    status = request.GET.get("status")
    start_date = request.GET.get("start_date")
    end_date = request.GET.get("end_date")

    # Query the LeaveRequest model with filters
    query = {}
    if not request.user.is_superuser:
        query["user"] = request.user

    if leave_type:
        query["leave_type"] = leave_type
    if status:
        query["status"] = status


    leave_requests = LeaveRequest.objects.filter(**query).order_by("-created_at")

    paginator = Paginator(leave_requests, 20)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    # Extract unique leave types and statuses for filtering
    leave_types = sorted(set(lr.leave_type for lr in LeaveRequest.objects.all()))
    statuses = sorted(set(lr.status for lr in LeaveRequest.objects.all()))

    leave_balance = None
    try:
        employee = Employee.objects.get(email=request.user.email)
        print(employee)
        leave_balance = employee.leave_balance
    except Employee.DoesNotExist:
        leave_balance = "0.00"

    context = {
        'page_obj': page_obj,  # Paginated leave requests
        'leave_types': leave_types,
        'statuses': statuses,
        'leave_balance': leave_balance,
        'filters': {
            'leave_type': leave_type,
            'status': status,
            'start_date': start_date,
            'end_date': end_date,
        },
    }

    return render(request, 'leave_requests_list.html', context)


@login_required
def edit_leave_request(request, leave_id):
    leave_request = get_object_or_404(LeaveRequest, id=int(leave_id))
    if request.method == "POST":

        leave_type = request.POST.get("leave_type")
        start_date = request.POST.get("start_date")
        end_date = request.POST.get("end_date")
        reason = request.POST.get("reason")
        status = request.POST.get("status")

        attachment = request.FILES.get("attachment")
        file_url = save_file_in_local(attachment)

        if file_url is not None:
            leave_request.attachment = file_url
        leave_request.leave_type = leave_type
        leave_request.start_date = start_date
        leave_request.end_date = end_date
        leave_request.reason = reason
        leave_request.status = status
        leave_request.save()

        messages.success(request, "Leave request updated successfully!")
        return redirect("leave_requests_list")

    context = {
        "leave_request": leave_request
    }

    return render(request, "leave_request_edit.html", context)

@login_required
def delete_leave_request(request, leave_id):
    leave_request = get_object_or_404(LeaveRequest, id=int(leave_id))
    leave_request.delete()
    messages.success(request, "Leave request deleted successfully!")
    return redirect("leave_requests_list")


@login_required
def get_leave_balance(request, id):
    leave_request = get_object_or_404(LeaveRequest, id=int(leave_id))
    context = {
        "leave_request": leave_request
    }
    return render(request, "leave_request_view.html", context)