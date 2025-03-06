from django.db import models

# Create your models here.
from django.db import models
from django.utils.timezone import now
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    phone = models.CharField(max_length=15, blank=True, null=True)
    gender_choices = [('male', 'Male'), ('female', 'Female'), ('other', 'Other')]
    gender = models.CharField(max_length=10, choices=gender_choices, blank=True, null=True)
    email = models.EmailField(blank=True, max_length=254, verbose_name='email address')
    username = models.CharField(max_length=150, unique=True, null=True, blank=True)

    def __str__(self):
        return self.email

class Property(models.Model):
    PROPERTY_TYPES = [
        ('apartment', 'Apartment'), ('villa', 'Villa'), ('home', 'Home'),
        ('office', 'Office'), ('building', 'Building'), ('townhouse', 'Townhouse'),
        ('shop', 'Shop'), ('garage', 'Garage')
    ]
    status_choices = [('available', 'Available'),('rent','Rent') ,('sale','Sale'),('sold', 'Sold')]
    p_status = models.CharField(max_length=50, choices=status_choices, default='available')
    p_name = models.CharField(max_length=255)
    p_type = models.CharField(max_length=50, choices=PROPERTY_TYPES)
    p_location = models.CharField(max_length=255)
    p_price = models.DecimalField(max_digits=10, decimal_places=2)
    p_bedrooms = models.IntegerField(default=1)
    p_bathrooms = models.IntegerField(default=1)
    p_images = models.ImageField(upload_to='property_images/')
    p_description = models.TextField()
    p_sqrft = models.IntegerField(default=1)
    p_user = models.ForeignKey(User, on_delete=models.CASCADE,null=True, blank=True)
    posted_on = models.DateTimeField(default=now)
    
    def __str__(self):
        return self.p_name
    

class Inquiry(models.Model):
    property = models.ForeignKey(Property, on_delete=models.CASCADE)
    sender_name = models.CharField(max_length=255, blank=True, null=True)
    sender_email = models.EmailField(max_length=254, blank=True, null=True)
    sender_phone = models.CharField(max_length=15, blank=True, null=True)
    message = models.TextField(max_length=10000)
    created_at = models.DateTimeField(default=now)

    def __str__(self):
        return f'Inquiry for {self.property.p_name} by {self.sender_name or "Unknown Sender"}'



class PropertyAttachment(models.Model):
    property = models.ForeignKey(Property, on_delete=models.CASCADE, blank=True, null=True)
    p_user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    ownership = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    town = models.CharField(max_length=100)
    street = models.CharField(max_length=255)
    contact_name = models.CharField(max_length=100)
    contact_email = models.EmailField(max_length=254)
    contact_phone = models.CharField(max_length=15)
    file = models.FileField(upload_to='property_attachments/', blank=True, null=True)

    def __str__(self):
        return f'Attachment for {self.property.p_name}' if self.property else 'Unassigned Attachment'

class Review(models.Model):
    reviewer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='given_reviews')
    seller = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_reviews')
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)])
    comment = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Review by {self.reviewer.email} for {self.seller.email} - {self.rating} stars'
    

class SavedProperty(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    property = models.ForeignKey(Property, on_delete=models.CASCADE)
    saved_on = models.DateTimeField(default=now)

    class Meta:
        unique_together = ('user', 'property')

    def __str__(self):
        return f"{self.user.username} - {self.property.p_name}"