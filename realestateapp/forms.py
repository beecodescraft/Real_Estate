from django import forms

from django.contrib.auth.models import User
from .models import Property, Inquiry, PropertyAttachment
from django.contrib.auth import get_user_model

User = get_user_model()  

class CustomerRegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}), required=True)
    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}), required=True)

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'phone', 'password', 'confirm_password', 'gender']

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password and confirm_password and password != confirm_password:
            raise forms.ValidationError("Passwords do not match.")

        return cleaned_data
# Property Form
class PropertyForm(forms.ModelForm):
    class Meta:
        model = Property
        fields = ['p_name', 'p_type', 'p_location', 'p_price', 'p_bedrooms', 'p_bathrooms', 'p_images', 'p_description', 'p_sqrft','p_status',]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Initially hide bedrooms and bathrooms for property types where they're not required
        self.fields['p_bedrooms'].required = False
        self.fields['p_bathrooms'].required = False
        
        # Add logic to dynamically show/hide fields based on property type
        if 'p_type' in self.data:
            property_type = self.data.get('p_type')
            if property_type not in ['home', 'townhouse']:
                self.fields['p_bedrooms'].widget.attrs['disabled'] = True
                self.fields['p_bathrooms'].widget.attrs['disabled'] = True
        elif self.instance.pk:
            if self.instance.p_type not in ['home', 'townhouse']:
                self.fields['p_bedrooms'].widget.attrs['disabled'] = True
                self.fields['p_bathrooms'].widget.attrs['disabled'] = True
    
    def clean(self):
        cleaned_data = super().clean()
        p_type = cleaned_data.get('p_type')
        p_bedrooms = cleaned_data.get('p_bedrooms')
        p_bathrooms = cleaned_data.get('p_bathrooms')

        # Ensure bedrooms and bathrooms are only required for certain property types
        if p_type in ['home', 'townhouse']:
            if not p_bedrooms or not p_bathrooms:
                raise forms.ValidationError("Bedrooms and bathrooms are required for Home and Townhouse properties.")
        return cleaned_data
    
class PropertyAttachmentForm(forms.ModelForm):
    class Meta:
        model = PropertyAttachment
        fields = [
            'property',
            'ownership',
            'state',
            'town',
            'street',
            'contact_name',
            'contact_email',
            'contact_phone'
        ]
        widgets = {
            'property': forms.Select(attrs={'class': 'form-select'}),  
            'ownership': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter ownership type'}),
            'state': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter the state'}),
            'town': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter the town'}),
            'street': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter the street address'}),
            'contact_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter contact name'}),
            'contact_email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Enter contact email'}),
            'contact_phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter contact phone number'}),
        }

    def clean_price(self):
        price = self.cleaned_data.get('price')
        if price <= 0:
            raise forms.ValidationError("Price must be greater than zero.")
        return price

    def clean_contact_phone(self):
        contact_phone = self.cleaned_data.get('contact_phone')
        if len(contact_phone) < 10:
            raise forms.ValidationError("Phone number should be at least 10 digits.")
        return contact_phone

class InquiryForm(forms.ModelForm):
    class Meta:
        model = Inquiry
        fields = [ 'sender_name', 'sender_email', 'sender_phone', 'message']
        widgets = {
            'sender_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter your name'}),
            'sender_email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Enter your email'}),
            'sender_phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter your phone number'}),
            'message': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Enter your message'}),
        }
   

class ProfileEditForm(forms.ModelForm):
    phone = forms.CharField(
        max_length=15, 
        required=False, 
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }

        
class EditPropertyForm(forms.ModelForm):
    class Meta:
        model = Property
        fields = [
             'p_name', 'p_type', 'p_location', 'p_price', 'p_bedrooms', 'p_bathrooms', 'p_images', 'p_description', 'p_sqrft'
        ]
        widgets = {
            'p_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter property title'}),
            'p_description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Enter property description'}),
            'p_price': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter price'}),
            'p_bedrooms': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Number of bedrooms'}),
            'p_bathrooms': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Number of bathrooms'}),
            'p_location': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter location'}),
            'p_type': forms.Select(attrs={'class': 'form-select'}),
            'p_images': forms.FileInput(attrs={'class': 'form-control'}),
            'p_sqrft': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter square footage'}),
        }

       

class DeleteAccountForm(forms.Form):
    confirm = forms.BooleanField(
        required=True,
        label="I confirm that I want to delete my account.",
    )