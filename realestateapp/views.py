from django.shortcuts import render, redirect,get_object_or_404
from django.contrib.auth import authenticate, login,logout
from django.contrib import messages
from .form import CustomerRegistrationForm,PropertyForm,ProfileEditForm,PropertyAttachmentForm,DeleteAccountForm
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Property, UserActivity,User,PropertyAttachment,Inquiry
from django.http import HttpResponseRedirect
from django.core.mail import send_mail

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
            return redirect('home')  # Redirect to homepage after registration

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
    properties = Property.objects.exclude(p_images="")
    attachments = PropertyAttachment.objects.filter(property=property_instance)
    # Debugging output
    print(f"Attachments for {property_instance.p_name}: {attachments}")

    context = {
        'attachments': attachments,
        'properties': properties,
        'property_instance': property_instance,
        'owner': property_instance.p_user ,
       }
    return render(request, 'details_property.html', context)


@login_required
def delete_property(request, property_id):
    property_obj = get_object_or_404(Property, pk=property_id)
    
    # Optional: Ensure only the owner can delete
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
            property_instance.p_user = request.user  # ✅ Assigns the logged-in user
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
            property_instance.p_user = request.user  
            attachment.property = property_instance  # Assign property
            attachment.save()
            print("Form submitted successfully!")
            return redirect('my_properties')  
        else:
            print(form.errors)  # Debugging errors
    
    else:
        form = PropertyAttachmentForm(initial={'property': property_instance})  # ✅ Prefill form
    
    return render(request, 'profile/additional_details_property.html', {'form': form, 'property': property_instance})

@login_required
def edit_property(request, property_id):
    property_obj = get_object_or_404(Property, id=property_id)

    if request.method == "POST":
        form = PropertyForm(request.POST, request.FILES, instance=property_obj)
        if form.is_valid():
            form.save()
            return redirect('profile/additional_details_property')  # Redirect after saving
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
    # Get properties the user has inquired about
    inquiries = Inquiry.objects.filter(sender=request.user).select_related("property")

    booked_properties = [inquiry.property for inquiry in inquiries]

    context = {
        'user': request.user,
        'contacted_properties': booked_properties,  # Send booked properties to the template
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
    user_properties = Property.objects.filter(p_user=request.user)  # Filter by logged-in user
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
    keyword = request.GET.get('keyword', '')
    property_type = request.GET.get('property_type', '')
    location = request.GET.get('location', '')

    # Apply filters based on search parameters
    if keyword:
        properties = properties.filter(description__icontains=keyword)
    if property_type:
        properties = properties.filter(property_type=property_type)
    if location:
        properties = properties.filter(location=location)

    return render(request, 'property_search.html', {'properties': properties})

@login_required
def send_inquiry(request, property_id):
    property_instance = get_object_or_404(Property, id=property_id)
    owner = property_instance.p_user 

    if request.method == "POST":
        message = request.POST.get("message")
        Inquiry.objects.create(
            sender=request.user,
            receiver=owner,
            property=property_instance,
            message=message
        )

        # Send email notification to the owner
        send_mail(
            "New Property Inquiry",
            f"Hello {owner.username},\n\nYou have received an inquiry for your property: {property_instance.p_name}.\n\nMessage: {message}\n\nFrom: {request.user.username}",
            "noreply@example.com",
            [owner.email],
            fail_silently=True,
        )
        

        return HttpResponseRedirect(request.META.get("HTTP_REFERER", "/"))

    return HttpResponseRedirect("/")

@login_required
def inquiry_list(request):
    inquiries = Inquiry.objects.filter(receiver=request.user)  # Show only received inquiries
    return render(request, "inquiries.html", {"inquiries": inquiries})


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