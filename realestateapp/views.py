from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, redirect,get_object_or_404
from django.contrib.auth import authenticate, login,logout
from django.contrib import messages
from .forms import CustomerRegistrationForm,PropertyForm,ProfileEditForm,PropertyAttachmentForm,DeleteAccountForm,InquiryForm
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Property,User,PropertyAttachment,Inquiry,SavedProperty
from django.template.loader import render_to_string
from django.core.mail import EmailMessage
import logging
from django.core.mail import send_mail
from django.conf import settings
from django.urls import reverse




def register(request):
    if request.method == 'POST':
        form = CustomerRegistrationForm(request.POST)
        if form.is_valid():
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']

            # Check if the email is already in use
            if User.objects.filter(email=email).exists():
                messages.error(request, "Email already registered. Try logging in.")
                return render(request, 'register.html', {'form': form})

            # Create user with default User model
            user = User.objects.create_user(
                username=email,  # Using email as the username
                email=email,
                first_name=first_name,
                last_name=last_name,
                password=password  # Password will be hashed automatically
            )

            # Log in the user immediately after registration
            login(request, user)
            messages.success(request, "Registration successful! Redirecting to home page...")
            return redirect('home') 

    else:
        form = CustomerRegistrationForm()

    return render(request, 'register.html', {'form': form})


def user_login(request):
    if request.method == "POST":
        email = request.POST.get('email')
        password = request.POST.get('password')

        # Authenticate user
        user = authenticate(request, username=email, password=password)

        if user is not None:
            login(request, user)
            return redirect('home')  # Change to your homepage or dashboard URL
        else:
            messages.error(request, "Invalid email or password. Please try again.")

    return render(request, 'login.html')

def user_logout(request):
    logout(request)
    return redirect('login') 


def home(request):
    properties = Property.objects.all()  # Get all properties

    # Get search parameters from the request
    location = request.GET.get('location', '')
    property_type = request.GET.get('property_type', '')

    # Apply filters if values are provided
    if location:
        properties = properties.filter(p_location__icontains=location)
    if property_type:
        properties = properties.filter(p_type=property_type)

    context = {
        'properties': properties,
    }
    return render(request, 'home.html', context)

def about(request):
    return render(request, 'profile/about.html')

def property_list(request):
    """View to display all properties"""
    properties = Property.objects.all()
    return render(request, 'list_property.html', {'properties': properties})

def property_detail(request, property_id):
    property_instance = get_object_or_404(Property, id=property_id)
    properties = Property.objects.exclude(p_images__isnull=True).exclude(p_images="")
    attachments = PropertyAttachment.objects.filter(property=property_instance)

    context = {
        'attachments': attachments,
        'properties': properties,
        'property_instance': property_instance,
        'owner': property_instance.p_user,
    }
    return render(request, 'details_property.html', context)

@login_required
def delete_property(request, property_id):
    property_obj = get_object_or_404(Property, pk=property_id)
    
  
    if request.user != property_obj.owner:
        messages.error(request, "You are not authorized to delete this property.")
        return redirect('details_property', property_id=property_id)

    property_obj.delete()
    messages.success(request, "Property deleted successfully.")
    return redirect('my_properties') 



@login_required
def add_property(request):
    if request.method == "POST":
        form = PropertyForm(request.POST, request.FILES)
        if form.is_valid():
            property_instance = form.save(commit=False)
            property_instance.p_user = request.user  
            property_instance.save()
            return redirect('additional_details_property', property_id=property_instance.id)
        else:
            print("Form errors:", form.errors)

    else:
        form = PropertyForm()

    return render(request, 'profile/add_property.html', {'form': form})
@login_required
def additional_details_property(request, property_id):
    property_instance = get_object_or_404(Property, id=property_id)
    
    if request.method == "POST":
        form = PropertyAttachmentForm(request.POST, request.FILES)
        if form.is_valid():
            attachment = form.save(commit=False)
            attachment.p_user = request.user  # Assigning the user as ForeignKey
            attachment.property = property_instance  # Assign property
            attachment.save()
            print("Form submitted successfully!")
            return redirect('my_properties')  
        else:
            print(form.errors)  # Debugging errors
    
    else:
        form = PropertyAttachmentForm(initial={'property': property_instance})  
    
    return render(request, 'profile/additional_details_property.html', {'form': form, 'property': property_instance})

@login_required
def edit_property(request, property_id):
    property_obj = get_object_or_404(Property, id=property_id)

    if request.method == "POST":
        form = PropertyForm(request.POST, request.FILES, instance=property_obj)
        if form.is_valid():
            form.save()
            return redirect(reverse('my_properties'))
    else:
        form = PropertyForm(instance=property_obj)

    return render(request, 'profile/edit_property.html', {'form': form})


@login_required
def delete_property(request, property_id):
    """View to delete a property (only for the owner)"""
    property_obj = get_object_or_404(Property, pk=property_id, p_user=request.user)
    if request.method == 'POST':
        property_obj.delete()
        return redirect('my_properties')
    return render(request, 'properties/delete_property.html', {'property': property_obj})



#profile view
@login_required
def profile(request):
    # Get properties the user has inquired about (fix applied)
    inquiries = Inquiry.objects.filter(sender_email=request.user.email).select_related("property")

    context = {
        'user': request.user,
        'inquiries': inquiries,  # Add inquiries to context
    }
    return render(request, 'profile/profile.html', context)
@login_required
def edit_profile(request):
    if request.method == 'POST':
        form = ProfileEditForm(request.POST, instance=request.user)  # Edit the User model directly
        if form.is_valid():
            form.save()
            return redirect('home') 
    else:
        form = ProfileEditForm(instance=request.user)  # Show existing user data

    return render(request, 'profile/edit_profile.html', {'form': form})

@login_required
def my_properties(request):
    """ View to display only the properties posted by the logged-in user """
    user_properties = Property.objects.filter(p_user=request.user)  
    return render(request, 'my_properties.html', {'properties': user_properties})

@login_required
def delete_account(request):
    if request.method == "POST":
        form = DeleteAccountForm(request.POST)
        if form.is_valid():
            user = request.user
            user.delete()  # Delete the user account
            logout(request)  # Log out the user
            messages.success(request, "Your account has been deleted successfully.")
            return redirect("home")  # Redirect to home page (update as needed)
    else:
        form = DeleteAccountForm()

    return render(request, "profile/delete.html", {"form": form})

def property_search(request):
    properties = Property.objects.all()  # Initially show all properties

    # Get search inputs
    keyword = request.GET.get('keyword', '').strip()
    p_type = request.GET.get('p_type', '').strip()
    p_location = request.GET.get('p_location', '').strip()

    # Apply filters
    if keyword:
        properties = properties.filter(p_name__icontains=keyword)  # Search by name
    if p_type:
        properties = properties.filter(p_type=p_type)  # Exact match for type
    if p_location:
        properties = properties.filter(p_location__icontains=p_location)  # Partial match for location

    return render(request, 'home.html', {'properties': properties, 'search_performed': True})


logger = logging.getLogger(__name__)

@login_required
def send_inquiry(request, property_id):
    property_obj = get_object_or_404(Property, id=property_id)
    owner = property_obj.p_user  

    if request.method == "POST":
        form = InquiryForm(request.POST)
        if form.is_valid():
            inquiry = form.save(commit=False)
            inquiry.property = property_obj
            inquiry.sender = request.user
            inquiry.receiver = owner
            inquiry.save()

            # Ensure property owner exists and has an email
            if not owner or not owner.email:
                messages.error(request, "The property owner does not have an email available.")
                return redirect('property_detail', property_id=property_id)

            logger.info(f"📧 Sending email to: {owner.email}")

            # Get sender details (customer making the inquiry)
            sender_email = request.user.email
            sender_name = request.user.username
            sender_phone = inquiry.sender_phone if inquiry.sender_phone else "Not available"

            # Render email content
            email_content = render_to_string('inquiry.txt', {
                'property': property_obj,
                'sender_name': sender_name,  # Customer (inquirer)
                'sender_email': sender_email,
                'sender_phone': sender_phone,
                'receiver_name': owner.username,  # Property owner
                'receiver_email': owner.email,
                'message': inquiry.message
            })

            try:   
                email = EmailMessage(
                subject=f"New Inquiry for {property_obj.p_name}",
                body=email_content,
                from_email=settings.EMAIL_HOST_USER,  # Sender (must be correct)
                to=[owner.email.strip()],  # Ensure it's a clean email
                )
                email.send()
                logger.info("✅ Email sent successfully.")
                return redirect('property_detail', property_id=property_id)


            except Exception as e:
                logger.error(f"❌ Failed to send email: {e}")
                messages.error(request, "Failed to send the inquiry email. Please try again later.")

    else:
        form = InquiryForm()

    return render(request, 'profile/inquiry_form.html', {'form': form, 'property': property_obj})

def help_page(request):
    if request.method == "POST":
        name = request.POST.get('name')
        email = request.POST.get('email')
        message = request.POST.get('message')

        subject = f"Help Request from {name}"
        full_message = f"Sender: {name}\nEmail: {email}\n\nMessage:\n{message}"

        send_mail(
            subject,
            full_message,
            'yourbusiness@example.com',  # Replace with your business email
            ['support@example.com'],  # Replace with the support email
            fail_silently=False,
        )

        messages.success(request, "Your message has been sent! We'll get back to you soon.")
        return redirect('help')

    return render(request, 'help.html')


@login_required
def save_property(request, property_id):
    property = get_object_or_404(Property, id=property_id)
    saved_property, created = SavedProperty.objects.get_or_create(user=request.user, property=property)

    if created:
        messages.success(request, "Property saved successfully!")
    else:
        messages.info(request, "This property is already in your saved list.")

    return redirect('property_detail', property_id=property.id)  # Redirect to property detail page

@login_required
def saved_properties(request):
    saved_list = SavedProperty.objects.filter(user=request.user)
    return render(request, 'saved_properties.html', {'saved_list': saved_list})