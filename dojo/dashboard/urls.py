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
from django.urls import path

from dashboard.views import (
    StudentDashboard,
    StudentProfile,
    SenseiDashboard,
    ManageTrainings,
    ManageTechniques,
    ManageStudents,
    ManageProfile,
    Library,
    Techniques,
    KataSeries,
    KataDetail,
    KataLessonDetail,
)

urlpatterns = [
    path('', SenseiDashboard.as_view(), name='sensei_dashboard'),
    path('manage_trainings/', ManageTrainings.as_view(), name='manage_trainings'),
    path('manage_techniques/', ManageTechniques.as_view(), name='manage_techniques'),
    path('manage_students/', ManageStudents.as_view(), name='manage_students'),
    path('manage_profile/<int:pk>/', ManageProfile.as_view(), name='manage_profile'),
    path('student/', StudentDashboard.as_view(), name='student_dashboard'),
    path('student/profile/', StudentProfile.as_view(), name='profile'),
    path('library/', Library.as_view(), name='library'),
    path('library/series/', KataSeries.as_view(), name='series'),
    path('library/techniques/', Techniques.as_view(), name='techniques'),
    path('library/kata/<int:pk>/', KataDetail.as_view(), name='kata_detail'),
    path('library/kata/lesson/<int:pk>/', KataLessonDetail.as_view(), name='kata_lesson_detail'),
]
