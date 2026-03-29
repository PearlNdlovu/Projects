from django.db import models
from django.contrib.auth.models import User
import uuid
import random
import string


def generate_reference():
    """Generate a unique reference number like SD-2024-XXXXX."""
    chars = string.ascii_uppercase + string.digits
    suffix = ''.join(random.choices(chars, k=6))
    from django.utils import timezone
    year = timezone.now().year
    return f"SD-{year}-{suffix}"


class Complaint(models.Model):
    CATEGORY_CHOICES = [
        ('water', 'Water & Sanitation'),
        ('electricity', 'Electricity & Load Shedding'),
        ('roads', 'Roads & Potholes'),
        ('waste', 'Waste & Refuse Collection'),
        ('housing', 'Housing & Property'),
        ('parks', 'Parks & Recreation'),
        ('safety', 'Public Safety & Lighting'),
        ('other', 'Other'),
    ]

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('submitted', 'Submitted'),
        ('in_progress', 'In Progress'),
        ('resolved', 'Resolved'),
        ('closed', 'Closed'),
    ]

    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ]

    reference_number = models.CharField(max_length=20, unique=True, default=generate_reference, editable=False)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='complaints')
    is_anonymous = models.BooleanField(default=False)

    # Personal details (optional if anonymous)
    first_name = models.CharField(max_length=100, blank=True)
    last_name = models.CharField(max_length=100, blank=True)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=20, blank=True)

    # Complaint details
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='other')
    title = models.CharField(max_length=200)
    description = models.TextField()
    location_address = models.CharField(max_length=300)
    ward_number = models.CharField(max_length=10, blank=True)

    # Media
    photo = models.ImageField(upload_to='complaints/', null=True, blank=True)

    # Status & priority
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium')

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    resolved_at = models.DateTimeField(null=True, blank=True)

    # Admin notes
    admin_notes = models.TextField(blank=True)
    assigned_to = models.CharField(max_length=100, blank=True)

    # Contact preferences
    notify_whatsapp = models.BooleanField(default=False)
    notify_email = models.BooleanField(default=True)
    notify_sms = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.reference_number} - {self.title}"

    def get_status_percentage(self):
        percentages = {
            'pending': 10,
            'submitted': 25,
            'in_progress': 60,
            'resolved': 90,
            'closed': 100,
        }
        return percentages.get(self.status, 0)


class ComplaintUpdate(models.Model):
    """Timeline of updates for a complaint."""
    complaint = models.ForeignKey(Complaint, on_delete=models.CASCADE, related_name='updates')
    message = models.TextField()
    updated_by = models.CharField(max_length=100, default='System')
    timestamp = models.DateTimeField(auto_now_add=True)
    new_status = models.CharField(max_length=20, blank=True)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"Update for {self.complaint.reference_number} at {self.timestamp}"


class Rating(models.Model):
    """User ratings for service delivery."""
    complaint = models.OneToOneField(Complaint, on_delete=models.CASCADE, related_name='rating')
    stars = models.IntegerField(default=0)
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Rating {self.stars}/5 for {self.complaint.reference_number}"
