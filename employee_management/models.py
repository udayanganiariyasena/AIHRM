from django.contrib.auth.models import User
from djongo import models

class Employee(models.Model):
    STATUS_CHOICES = [
        (0, 'Disable'),
        (1, 'Enable'),
    ]

    id = models.ObjectIdField(primary_key=True)  # MongoDB ObjectId as primary key
    full_name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15)
    address = models.TextField()
    date_of_birth = models.DateField()
    joining_date = models.DateField()
    department = models.CharField(max_length=100)
    role = models.CharField(max_length=100)
    basic_salary = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    allowance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    status = models.SmallIntegerField(choices=STATUS_CHOICES, default=1)
    is_staff = models.SmallIntegerField(choices=STATUS_CHOICES, default=0)

    def __str__(self):
        return self.full_name

    class Meta:
        db_table = "employees"
        ordering = ["-joining_date"]


class EmployeeAttendance(models.Model):
    id = models.ObjectIdField(primary_key=True)
    employee = models.CharField(max_length=255)
    employee_ref = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField()
    status = models.CharField(max_length=50, choices=[("Present", "Present"), ("Absent", "Absent")])

    objects = models.DjongoManager()