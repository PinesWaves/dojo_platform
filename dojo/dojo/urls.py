from django.contrib import admin
from django.contrib.auth.views import LoginView
from django.shortcuts import redirect
from django.urls import path, include

from user_management.views import RegisterView

urlpatterns = [
    path('', lambda request: redirect('login/')),
    path('login/', LoginView.as_view(template_name='login_register/login.html', next_page='index'), name='login'),
    path('signup/', RegisterView.as_view(), name='signup'),
    # path("attendance/", include('application.urls')),
    path('admin/', admin.site.urls),
]
