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

from dashboard.views import (
    SenseiDashboard,
    StudentDashboard,
    ManageTrainingsView,
    ManageTechniquesView,
    ManageStudentsView
)

urlpatterns = [
    path('', SenseiDashboard.as_view(), name='sensei_dashboard'),
    path('student/', StudentDashboard.as_view(), name='student_dashboard'),
    path('manage_trainings/', ManageTrainingsView.as_view(), name='manage_trainings'),
    path('manage_techniques/', ManageTechniquesView.as_view(), name='manage_techniques'),
    path('manage_students/', ManageStudentsView.as_view(), name='manage_students'),
]
