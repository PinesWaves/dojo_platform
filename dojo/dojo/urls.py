from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth.views import LogoutView
from django.urls import path, include

from .views import landing_page, custom_404, custom_500
from user_management.views import RegisterView, CustomLoginView, RecoverPass, ForgotPass, CustomLogoutView

urlpatterns = [
    path('', landing_page, name='landing'),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', CustomLogoutView.as_view(next_page='login'), name='logout'),
    path('signup/<str:token>/', RegisterView.as_view(), name='signup'),
    path('forgot-password/', ForgotPass.as_view(), name='forgot-password'),
    path('recover-password/<str:token>/', RecoverPass.as_view(), name='recover-password'),
    path('dashboard/', include('dashboard.urls')),
    path('404/', custom_404, name='404'),
    path('500/', custom_500, name='500'),
]

# Solo habilita el admin si DEBUG=True o ALLOW_ADMIN=True
if settings.DEBUG or getattr(settings, 'ALLOW_ADMIN', False):
    from django.contrib import admin

    urlpatterns += [
        path('admin/', admin.site.urls),
    ]

if settings.DEBUG:
    from django.shortcuts import render

    def test_404(request):
        return render(request, 'errors/404.html', status=404)

    def test_500(request):
        return render(request, 'errors/500.html', status=500)

    urlpatterns += [
        path('test-404/', test_404, name='test_404'),
        path('test-500/', test_500, name='test_500'),
    ]
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

handler404 = 'dojo.views.custom_404'
handler500 = 'dojo.views.custom_500'
