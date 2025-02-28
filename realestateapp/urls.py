
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView
from .views import home,about,register,help_page, profile,edit_profile ,property_list,add_property,my_properties,edit_property,property_detail,additional_details_property,delete_property,user_login,user_logout,delete_account,send_inquiry, inquiry_list



urlpatterns = [
    path('register/', register, name='register'),  # Existing register view
    path('login/', user_login, name='login'),  
    path('logout/', user_logout, name='logout'),
    path('home/', home, name='home'),
    path('about/', about, name='about'),
    path('profile/', profile, name='profile'),
    path('edit-profile/', edit_profile, name='edit_profile'),
    path('list_property/', property_list, name='property_list'),
    path('edit_property/<int:property_id>/', edit_property, name='edit_property'),
    path('my_properties/', my_properties, name='my_properties'),
    path('add_property/', add_property, name='add_property'),
    path('details_property/<int:property_id>/',property_detail , name='property_detail'),
    path('additional-details/<int:property_id>/', additional_details_property, name='additional_details_property'),
    path('delete_property/<int:property_id>/', delete_property, name='delete_property'),
    path("delete/", delete_account, name="delete_account"),
    path('send-inquiry/<int:property_id>/', send_inquiry, name='send_inquiry'),
    path("inquiries/",  inquiry_list, name="inquiry_list"),
    path('help/', help_page, name='help'),

]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)