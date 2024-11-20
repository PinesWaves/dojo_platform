from django.contrib import admin
from django.contrib.auth.views import LoginView
from django.shortcuts import redirect
from django.urls import path, include

from user_management.views import RegisterView, CustomLoginView

urlpatterns = [
    path('', lambda request: redirect('login/')),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('signup/', RegisterView.as_view(), name='signup'),
    path("dashboard/", include('application.urls')),
    path('admin/', admin.site.urls),
]
