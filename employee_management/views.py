from decimal import Decimal

from django.contrib import admin
from django.contrib.auth.models import User, Group
from django.shortcuts import render, redirect, get_object_or_404
from datetime import datetime
from django.core.paginator import Paginator
from datetime import datetime
from django.shortcuts import render
from django.contrib.admin import site as admin_site
from django.contrib import messages
from datetime import datetime
from django.contrib.auth.decorators import login_required

from employee_management.models import Employee, EmployeeAttendance


@login_required
def index(request):
    # Retrieve filter parameters from the request
    department = request.GET.get("department")
    role = request.GET.get("role")
    status = request.GET.get("status")
    joined_date = request.GET.get("joined_date")

    # Query the Employee model
    query = {"is_staff": 0}
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

    return render(request, 'index.html', context)


@login_required
def create(request):
    if request.method == "POST":
        
        names = request.POST.getlist('employee-name[]')
        emails = request.POST.getlist('employee-email[]')
        epf_numbers = request.POST.getlist('employee-epf[]')
        phones = request.POST.getlist('employee-phone[]')
        addresses = request.POST.getlist('employee-address[]')
        dobs = request.POST.getlist('employee-dob[]')
        join_dates = request.POST.getlist('employee-joining-date[]')
        departments = request.POST.getlist('employee-department[]')
        roles = request.POST.getlist('employee-role[]')
        passwords = request.POST.getlist('employee-password[]')
        basic_salaries = request.POST.getlist('employee-basic_salary[]')
        leave_balance = request.POST.getlist('employee-leave-balance[]')
        allowances = request.POST.getlist('employee-allowances[]')
        staff_statuses = request.POST.getlist('employee-staff-status[]')

        employees_created = 0
        errors = []

        # Validate and process each employee
        for i in range(len(names)):
            name = names[i].strip()
            email = emails[i].strip()
            epf_number = epf_numbers[i].strip()
            phone = phones[i].strip()
            address = addresses[i].strip()
            dob = dobs[i].strip()
            join_date = join_dates[i].strip()
            department = departments[i].strip()
            role = roles[i].strip()
            password = passwords[i].strip()
            basic_salary = basic_salaries[i].strip()
            leave_balance = leave_balance[i].strip()
            allowance = allowances[i].strip()
            is_staff = staff_statuses[i].strip()

            # Validate required fields
            if not name or not email or not phone:
                errors.append(f"Error for Employee {i + 1}: Missing required fields.")
                continue

            # Try to save the employee
            try:
                employee = Employee(
                    full_name=name,
                    email=email,
                    epf_number=epf_number,
                    phone=phone,
                    address=address,
                    date_of_birth=datetime.strptime(dob, '%Y-%m-%d'),
                    joining_date=datetime.strptime(join_date, '%Y-%m-%d'),
                    department=department,
                    role=role,
                    basic_salary=basic_salary,
                    allowance=allowance,
                    leave_balance=leave_balance,
                    is_staff=int(is_staff),
                )
                employee.save()
                employees_created += 1
                create_employee_login(employee, password)
            except Exception as e:
                errors.append(f"Error for Employee {i + 1}: {e}")

        # Set messages for success and errors
        if employees_created:
            messages.success(request, f"{employees_created} employees registered successfully!")
        if errors:
            for error in errors:
                messages.error(request, error)

        return redirect('list_employees')  # Replace with your employee listing view's URL name

    return render(request, 'register.html')


@login_required
def mark_attendance(request):
    if request.method == "POST":
        # Retrieve data from the form
        employee_ids = request.POST.getlist("employee-id[]")
        attendance_dates = request.POST.getlist("attendance-date[]")
        statuses = request.POST.getlist("attendance-status[]")

        # Process each attendance record
        for i in range(len(employee_ids)):
            employee_id = employee_ids[i].strip()
            attendance_date = attendance_dates[i].strip()
            status = statuses[i].strip()

            employee = get_object_or_404(Employee, id=int(employee_id))

            userRef = User.objects.filter(username=employee.email).first()

            # Validate required fields
            if not employee_id or not attendance_date or not status:
                messages.error(request, f"Error in record {i + 1}: Missing required fields.")
                continue

            # Save the attendance record
            attendance_record = EmployeeAttendance(
                employee=employee_id,
                employee_ref=userRef,
                date=attendance_date,
                status=status
            )
            attendance_record.save()

        messages.success(request, "Attendance records marked successfully!")
        return redirect("attendance_list")
    query = {"is_staff": 0}
    employees = Employee.objects.filter(**query)
    context = {
        "employees": employees
    }
    return render(request, "mark_attendance.html", context)


@login_required
def attendance_list(request):
    # Get filter parameters
    employee_id = request.GET.get('employee')
    date = request.GET.get('date')
    status = request.GET.get('status')

    if request.user.is_superuser:
        attendance_records = EmployeeAttendance.objects.all()
    else:
        attendance_records = EmployeeAttendance.objects.filter(employee_ref=request.user)

    # Apply filters
    if employee_id:
        attendance_records = attendance_records.filter(employee_id=employee_id)
    if date:
        attendance_records = attendance_records.filter(date=date)
    if status:
        attendance_records = attendance_records.filter(status=status)

    # Pagination
    paginator = Paginator(attendance_records, 10)  # 10 records per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Fetch all employees for the filter dropdown
    employees = Employee.objects.all()

    context = {
        'page_obj': page_obj,
        'employees': employees,
    }
    return render(request, 'attendance_list.html', context)


@login_required
def edit_employee(request, employee_id):
    # Get the employee object, or return a 404 error if not found
    employee = get_object_or_404(Employee, id=employee_id)

    if request.method == "POST":
        name = request.POST.get('employee-name')
        status = request.POST.get('employee-status')
        email = request.POST.get('employee-email')
        phone = request.POST.get('employee-phone')
        address = request.POST.get('employee-address')
        dob = request.POST.get('employee-dob')
        join_date = request.POST.get('employee-joining-date')
        department = request.POST.get('employee-department')
        role = request.POST.get('employee-role')
        basic_salary = Decimal(request.POST.get('employee-basic_salary', 0.00))
        allowance = Decimal(request.POST.get('employee-allowance', 0.00))
        password = request.POST.get('employee-password')
        leave_balance = request.POST.get('employee-leave-balance', 0.00)

        employee.full_name = name
        employee.email = email
        employee.phone = phone
        employee.address = address
        employee.date_of_birth = datetime.strptime(dob, '%Y-%m-%d')
        employee.joining_date = datetime.strptime(join_date, '%Y-%m-%d')
        employee.department = department
        employee.role = role
        employee.basic_salary = basic_salary
        employee.leave_balance = leave_balance
        employee.allowance = allowance
        employee.status = int(status)

        employee.save()
        update_employee_logins(password, employee)

        return redirect('list_employees')

    return render(request, 'edit_employee.html', {'employee': employee})


def create_employee_login(employee, password):
    """Creates a Django User for the given employee and assigns to Employee group."""

    # Check if the user already exists
    user = User.objects.filter(username=employee.email).first()

    if user is None:
        user = User.objects.create_user(
            username=employee.email,
            email=employee.email,
            password=password
        )
        user.first_name = employee.full_name
        if employee.is_staff == 1:
            user.is_staff = True
            user.is_superuser = True
        user.save()

        # Assign to Employee group
        employee_group, created = Group.objects.get_or_create(name="Employee")
        user.groups.add(employee_group)

        user.save()
    else:
        pass


def update_employee_logins(password, employee):
    user = User.objects.filter(username=employee.email).first()
    if user is None:
        user.username = employee.email
        user.first_name = employee.full_name
        user.email = employee.email
        if password is not None:
            user.password = password

        employee_status = True

        if employee.status == 0:
            employee_status = False

        if employee.is_staff == 1:
            user.is_staff = True
            user.is_superuser = True

        user.is_active = employee_status
        user.save()


@login_required
def edit_attendance(request, attendance_id):
    # Get the attendance record or return a 404 error if not found
    attendance = get_object_or_404(EmployeeAttendance, id=attendance_id)

    if request.method == "POST":
        attendance_date = request.POST.get("attendance-date")
        status = request.POST.get("attendance-status")

        # Validate required fields
        if not attendance_date or not status:
            messages.error(request, "All fields are required.")
            return redirect("attendance_list", attendance_id=attendance.id)

        attendance.date = attendance_date
        attendance.status = status
        attendance.save()

        messages.success(request, "Attendance record updated successfully!")
        return redirect("attendance_list")

    employees = Employee.objects.all()
    context = {
        "attendance": attendance,
        "employees": employees,
    }
    return render(request, "edit_attendance.html", context)


@login_required
def delete_attendance(request, attendance_id):
    # Get the attendance record or return a 404 error if not found
    attendance = get_object_or_404(EmployeeAttendance, id=attendance_id)

    attendance.delete()
    messages.success(request, "Attendance record deleted successfully!")
    return redirect("attendance_list")
