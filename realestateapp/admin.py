from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Property, UserActivity, Review, Inquiry, PropertyAttachment
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _

User = get_user_model()

class CustomUserAdmin(UserAdmin):
    model = User
    list_display = ('email', 'first_name', 'last_name', 'is_staff', 'is_active')
    list_filter = ('is_staff', 'is_superuser', 'is_active')

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'phone', 'gender')}),
        (_('Permissions'), {'fields': ('is_staff', 'is_active', 'is_superuser', 'groups', 'user_permissions')}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'first_name', 'last_name', 'phone', 'gender', 'password1', 'password2', 'is_staff', 'is_active')}
        ),
    )

    search_fields = ('email', 'first_name', 'last_name')
    ordering = ('email',)  # ✅ Fix the ordering issue
    filter_horizontal = ('groups', 'user_permissions')

# Register the custom UserAdmin
admin.site.register(User, CustomUserAdmin)

# Register other models
admin.site.register(Property)
admin.site.register(UserActivity)
admin.site.register(Review)
admin.site.register(Inquiry)
admin.site.register(PropertyAttachment)
