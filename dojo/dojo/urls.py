from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth.views import LoginView, LogoutView
from django.shortcuts import redirect
from django.urls import path, include

from . import views
from user_management.views import RegisterView, CustomLoginView

urlpatterns = [
    # path('', lambda request: redirect('login/')),
    path('', views.landing_page, name='landing'),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(next_page='login'), name='logout'),
    path('signup/<str:token>/', RegisterView.as_view(), name='signup'),
    path('dashboard/', include('dashboard.urls')),
    path('admin/', admin.site.urls, name='admin'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
