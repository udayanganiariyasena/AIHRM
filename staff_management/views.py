from django.core.paginator import Paginator
from django.shortcuts import render
from django.contrib.admin import site as admin_site
from datetime import datetime
from django.contrib.auth.decorators import login_required
from employee_management.models import Employee

@login_required
def index(request):
    # Retrieve filter parameters from the request
    department = request.GET.get("department")
    role = request.GET.get("role")
    status = request.GET.get("status")
    joined_date = request.GET.get("joined_date")

    # Query the Employee model
    query = {"is_staff": 1}
    if department:
        query["department"] = department
    if role:
        query["role"] = role
    if status:
        query["status"] = status
    if joined_date:
        try:
            filter_date = datetime.strptime(joined_date, "%Y-%m-%d")
            query["joining_date__gte"] = filter_date  # MongoDB equivalent for gte
        except ValueError:
            pass  # Ignore invalid date format

    employees = Employee.objects.filter(**query)

    # Set up pagination
    paginator = Paginator(employees, 5)  # Show 5 employees per page
    page_number = request.GET.get("page")  # Get current page number
    page_obj = paginator.get_page(page_number)  # Get employees for the current page

    # Extract unique departments and roles for filters
    departments = sorted(set(e.department for e in Employee.objects.all()))
    roles = sorted(set(e.role for e in Employee.objects.all()))

    context = {
        'available_apps': admin_site.get_app_list(request),
        'breadcrumbs': '',
        'page_obj': page_obj,  # Pass paginated data to the template
        'departments': departments,
        'roles': roles,
        'filters': {
            'department': department,
            'role': role,
            'status': status,
            'joined_date': joined_date,
        },
    }

    return render(request, 'staff_index.html', context)
