"""
URL configuration for EventManagement project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from main import views

from django.conf import settings
from django.conf.urls.static import static
urlpatterns = [

    path('admin/', admin.site.urls),

    path('index/', views.index, name='index'),

    path('events/', views.events, name='events'),

    path('about/', views.about, name='about'),

    path('contact/', views.contact, name='contact'),

    path('adminlogin/', views.admin, name='admin_login'),

    path('dashboard/', views.dashboard, name='admin_dashboard'),

    path('add-event/', views.add_event, name='add_event'),

    path('add-category/', views.add_category, name='add_category'),

    path('edit-category/<int:id>/', views.edit_category, name='edit_category'),

    path('delete-category/<int:id>/', views.delete_category, name='delete_category'),

    path('edit-event/<int:id>/', views.edit_event, name='edit_event'),

    path('delete-event/<int:id>/', views.delete_event, name='delete_event'),

    path('admin-logout/', views.admin_logout, name='admin_logout'),

    path('subscribe/', views.subscribe, name='subscribe'),

    path('book-event/<int:event_id>/',views.book_event, name='book_event'),

    path('approve-booking/<int:booking_id>/',views.approve_booking, name='approve_booking'),

    path('cancel-booking/<int:booking_id>/',views.cancel_booking, name='cancel_booking'),

    
  
]
if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT
    )