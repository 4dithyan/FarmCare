from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class District(models.Model):
    name = models.CharField(max_length=100, unique=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class UserProfile(models.Model):
    ROLE_CHOICES = [('farmer', 'Farmer'), ('admin', 'Admin')]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='farmer')
    phone = models.CharField(max_length=15, blank=True)
    location = models.CharField(max_length=200, blank=True, help_text="Village/Address")
    district = models.ForeignKey(District, on_delete=models.SET_NULL, null=True, blank=True)
    farm_size = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, help_text="Farm size in acres")
    profile_picture = models.ImageField(upload_to='profiles/', blank=True, null=True)
    bio = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username} ({self.role})"

    def is_admin(self):
        return self.role == 'admin'

    def is_farmer(self):
        return self.role == 'farmer'


class CardamomPrice(models.Model):
    GRADE_CHOICES = [
        ('8mm', '8mm'),
        ('7mm', '7mm'),
        ('6mm', '6mm'),
        ('bold', 'Bold'),
        ('medium', 'Medium'),
        ('small', 'Small'),
        ('other', 'Other'),
    ]

    market = models.CharField(max_length=200)
    grade = models.CharField(max_length=20, choices=GRADE_CHOICES, default='other')
    min_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    max_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    modal_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    unit = models.CharField(max_length=20, default='per kg')
    date = models.DateField(default=timezone.now)
    raw_data = models.TextField(blank=True)
    scraped_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date', 'market']
        verbose_name = 'Cardamom Price'
        verbose_name_plural = 'Cardamom Prices'

    def __str__(self):
        return f"{self.market} - {self.grade} - ₹{self.modal_price} ({self.date})"


class GalleryImage(models.Model):
    title = models.CharField(max_length=200)
    image = models.ImageField(upload_to='gallery/')
    caption = models.TextField(blank=True)
    category = models.CharField(max_length=50, choices=[
        ('farm', 'Farm'),
        ('harvest', 'Harvest'),
        ('processing', 'Processing'),
        ('community', 'Community'),
        ('other', 'Other'),
    ], default='farm')
    uploaded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_featured = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title


class DiseaseRecommendation(models.Model):
    disease_name = models.CharField(max_length=200, unique=True)
    description = models.TextField()
    symptoms = models.TextField()
    medicine = models.TextField()
    dosage = models.TextField(blank=True)
    precautions = models.TextField()
    severity = models.CharField(max_length=20, choices=[
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    ], default='medium')
    image = models.ImageField(upload_to='disease_images/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.disease_name} ({self.severity})"


class AIReport(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]

    farmer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ai_reports')
    image = models.ImageField(upload_to='ai_reports/')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    disease_detected = models.CharField(max_length=200, blank=True)
    confidence_level = models.CharField(max_length=50, blank=True)
    severity = models.CharField(max_length=50, blank=True)
    symptoms = models.TextField(blank=True)
    diagnosis = models.TextField(blank=True)
    medicines = models.TextField(blank=True)
    dosage = models.TextField(blank=True)
    precautions = models.TextField(blank=True)
    gemini_response = models.TextField(blank=True)
    expert_deep_dive = models.TextField(blank=True)
    is_cardamom = models.BooleanField(default=True)
    recommendation = models.ForeignKey(
        DiseaseRecommendation, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='reports'
    )
    additional_notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Report by {self.farmer.username} - {self.disease_detected or 'Pending'} ({self.created_at.date()})"


class SoilTestRequest(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('rejected', 'Rejected'),
    ]

    farmer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='soil_requests')
    farm_location = models.CharField(max_length=300)
    farm_size = models.DecimalField(max_digits=10, decimal_places=2, help_text="Size in acres")
    soil_type = models.CharField(max_length=100, blank=True)
    additional_info = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    admin_notes = models.TextField(blank=True)
    requested_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    scheduled_date = models.DateField(null=True, blank=True)

    class Meta:
        ordering = ['-requested_at']

    def __str__(self):
        return f"Soil Request by {self.farmer.username} - {self.status} ({self.requested_at.date()})"


class Announcement(models.Model):
    title = models.CharField(max_length=300)
    content = models.TextField()
    posted_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title


class TeamMember(models.Model):
    name = models.CharField(max_length=200)
    role = models.CharField(max_length=200)
    bio = models.TextField(blank=True)
    image = models.ImageField(upload_to='team/', blank=True, null=True)
    order = models.IntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"{self.name} - {self.role}"
