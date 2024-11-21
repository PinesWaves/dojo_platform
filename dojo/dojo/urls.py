from django.contrib import admin
from django.contrib.auth.views import LoginView, LogoutView
from django.shortcuts import redirect
from django.urls import path, include

from user_management.views import RegisterView, CustomLoginView

urlpatterns = [
    path('', lambda request: redirect('login/')),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(next_page='login'), name='logout'),
    path('signup/', RegisterView.as_view(), name='signup'),
    path("dashboard/", include('application.urls')),
    path('admin/', admin.site.urls),
]
