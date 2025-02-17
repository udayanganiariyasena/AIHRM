from django.contrib.auth.models import User
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator

from employee_management.models import Employee
from home.drive_upload import save_file_in_local
from django.contrib.admin import site as admin_site

from task_management.models import Task, TaskComment


@login_required
def create_task(request):

    context = {
        'available_apps': admin_site.get_app_list(request),
        'employees': Employee.objects.all(),
    }


    if request.method == "POST":
        try:

            attachment = request.FILES.get("image")
            file_url = save_file_in_local(attachment)
            employee_email = Employee.objects.get(id=int(request.POST.get('assignee'))).email

            task = Task(
                title=request.POST.get('title'),
                description=request.POST.get('description'),
                assignee=User.objects.get(email=employee_email),
                status=request.POST.get('status'),
                due_date=request.POST.get('due-date'),
                image=file_url,
            )
            task.save()
            messages.success(request, "Task created successfully!")
            return redirect("tasks_index")
        except Exception as e:
            messages.error(request, "Error creating task. Please check the form.")

    return render(request, 'task/create.html', context)


@login_required
def create_task_comment(request):
    if request.method == "POST":
        taskComment = TaskComment(
            task=Task.objects.get(id=int(request.POST.get('task'))),
            author=request.user,
            comment=request.POST.get('comment'),
        )
        taskComment.save()

        return redirect(request.META.get('HTTP_REFERER', 'default_view_name'))


@login_required
def edit_task(request, task_id):
    task = get_object_or_404(Task, id=int(task_id))

    if request.method == "POST":
        task.title = request.POST.get('title')
        task.description = request.POST.get('description')
        task.status = request.POST.get('status')
        task.due_date = request.POST.get('due-date')

        attachment = request.FILES.get("image")
        file_url = save_file_in_local(attachment)

        if file_url:
            task.image = file_url

        assignee_id = request.POST.get('assignee')
        if assignee_id:
            employee = Employee.objects.get(id=int(assignee_id))
            task.assignee = User.objects.get(email=employee.email)


        task.save()
        return redirect('tasks_index')  # Redirect to the task list or detail page

    context = {
        'task': task,
        'employees': Employee.objects.all(),
        'task_comments': TaskComment.objects.filter(task=task),
    }
    return render(request, 'task/edit.html', context)

@login_required
def index(request):
    if request.user.is_superuser:
        tasks = Task.objects.all()  # Superusers can see all tasks
    else:
        tasks = Task.objects.filter(assignee=request.user)

    # Apply filters
    assignee_id = request.GET.get('assignee')
    status = request.GET.get('status')
    created_after = request.GET.get('created_after')
    due_date = request.GET.get('due_date')

    if assignee_id:
        tasks = tasks.filter(assignee_id=assignee_id)

    if status:
        tasks = tasks.filter(status=status)

    if created_after:
        tasks = tasks.filter(created_at__gte=created_after)

    if due_date:
        tasks = tasks.filter(due_date=due_date)

    # Pagination
    paginator = Paginator(tasks, 20)  # Show 10 tasks per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    employees = Employee.objects.all()

    return render(request, 'task_index.html', {
        'page_obj': page_obj,
        'employees': employees
    })

@login_required
def delete_task(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    task.delete()
    messages.success(request, "Task deleted successfully.")
    return redirect('tasks_index')
