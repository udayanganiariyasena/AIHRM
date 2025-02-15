from djongo import models
from django.contrib.auth.models import User

class DocumentRequest(models.Model):
    DOCUMENT_TYPES = [
        ('Experience Letter', 'Experience Letter'),
        ('Salary Certificate', 'Salary Certificate'),
        ('Employment Verification', 'Employment Verification'),
        ('Other', 'Other'),
    ]

    SENT_STATUS_CHOICES = [
        (0, 'Not Sent'),
        (1, 'Sent'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    document_type = models.CharField(max_length=50, choices=DOCUMENT_TYPES)
    reason = models.TextField()
    status = models.CharField(
        max_length=20,
        choices=[('Pending', 'Pending'), ('Approved', 'Approved'), ('Rejected', 'Rejected')],
        default='Pending'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    sent_status = models.SmallIntegerField(choices=SENT_STATUS_CHOICES, default=0)

    def __str__(self):
        return f"{self.user.username} - {self.document_type} ({self.status})"
