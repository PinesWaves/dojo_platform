"""
URL configuration for dojo project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
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
from django.urls import path, include

from application.views import Dashboard, TemplateView

urlpatterns = [
    path('dashboard', Dashboard.as_view(), name='dashboard'),
    path('dashboard/sensei/', TemplateView.as_view(template_name="pages/sensei_dashboard.html"), name='sensei_dashboard'),
    path('dashboard/student/', TemplateView.as_view(template_name="pages/student_dashboard.html"), name='student_dashboard'),
]
