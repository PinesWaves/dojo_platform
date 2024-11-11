from django.contrib import admin
from django.shortcuts import redirect
from django.urls import path, include

urlpatterns = [
    path('', lambda request: redirect('https://seishinjkadojo.com/')),
    path('login/', include('user_management.urls')),
    path("attendance/", include('application.urls')),
    path('admin/', admin.site.urls),
]
