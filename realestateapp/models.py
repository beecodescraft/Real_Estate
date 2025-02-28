from django.db import models
from django.utils.timezone import now
from django.contrib.auth.models import AbstractUser



class User(AbstractUser):
    phone = models.CharField(max_length=15, blank=True, null=True)
    gender_choices = [('male', 'Male'), ('female', 'Female'), ('other', 'Other')]
    gender = models.CharField(max_length=10, choices=gender_choices, blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)

    username = models.CharField(
        max_length=150,
        unique=True,
        null=True,  # You can make this null if you want to use email for login
        blank=True,
    )

    def __str__(self):
        return self.email

# Property Model
class Property(models.Model):
    PROPERTY_TYPES = [
        ('apartment', 'Apartment'),
        ('villa', 'Villa'),
        ('home', 'Home'),
        ('office', 'Office'),
        ('building', 'Building'),
        ('townhouse', 'Townhouse'),
        ('shop', 'Shop'),
        ('garage', 'Garage'),
    ]
    STATUS_CHOICES = [
        ('sale', 'For Sale'),
        ('rent', 'For Rent'),
        ('sold', 'Sold'),
    ]
    
   
    p_name = models.CharField(max_length=255)
    p_type = models.CharField(max_length=50, choices=PROPERTY_TYPES)
    p_location = models.CharField(max_length=255)
    p_price = models.DecimalField(max_digits=10, decimal_places=2)
    p_bedrooms = models.IntegerField(default=1)
    p_bathrooms = models.IntegerField(default=1)
    p_images = models.ImageField(upload_to='property_images/')
    p_description = models.TextField()
    p_sqrft = models.IntegerField(default=1)
    p_user = models.ForeignKey(User, on_delete=models.CASCADE)
    p_status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='sale')
    created_at = models.DateTimeField(default=now)

    
    def __str__(self):
        return self.p_name

# Additional Property Details
class PropertyAttachment(models.Model):
    p_user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True) 
    property = models.ForeignKey(Property, on_delete=models.CASCADE, null=True, blank=True)
    ownership = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    town = models.CharField(max_length=100)
    street = models.CharField(max_length=255)
    contact_name = models.CharField(max_length=100)
    contact_email = models.EmailField()
    contact_phone = models.CharField(max_length=15)

    file = models.FileField(upload_to="property_attachments/", null=True, blank=True)
    
    def __str__(self):
         return f"Attachment for {self.property.p_name}" if self.property else "Unassigned Attachment"
    
class UserActivity(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    inquiries = models.ManyToManyField('Inquiry', blank=True)  # Track inquiries directly
    seen_properties = models.IntegerField(default=0)
    saved_properties = models.IntegerField(default=0)
    saved_searches = models.IntegerField(default=0)

    def __str__(self):
        return f"Activity of {self.user.username}"

# Review Model
class Review(models.Model):
    reviewer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='given_reviews')
    seller = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_reviews')
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)])  # Rating from 1 to 5
    comment = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Review by {self.reviewer.email} for {self.seller.email} - {self.rating} stars"

# Inquiry Model


class Inquiry(models.Model):
    message = models.TextField()
    property = models.ForeignKey('Property', on_delete=models.CASCADE)
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_inquiries',null=True, blank=True)  # Add this field
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_inquiries', null=True, blank=True)
    created_at = models.DateTimeField(default=now)

    def __str__(self):
        return f"Inquiry from {self.sender.username} to {self.receiver.username} about {self.property.p_name}"