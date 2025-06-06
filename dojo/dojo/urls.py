from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth.views import LogoutView
from django.urls import path, include

from .views import *
from user_management.views import RegisterView, CustomLoginView


urlpatterns = [
    path('', landing_page, name='landing'),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(next_page='login'), name='logout'),
    path('signup/<str:token>/', RegisterView.as_view(), name='signup'),
    path('dashboard/', include('dashboard.urls')),
    path('404/', custom_404),
    path('500/', custom_500),
]

# Solo habilita el admin si DEBUG=True o ALLOW_ADMIN=True
if settings.DEBUG or getattr(settings, 'ALLOW_ADMIN', False):
    from django.contrib import admin
    urlpatterns += [
        path('admin/', admin.site.urls),
    ]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

handler404 = 'dojo.views.custom_404'
handler500 = 'dojo.views.custom_500'
