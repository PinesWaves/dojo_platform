from django.shortcuts import render
from django.views.generic import TemplateView
import logging

logger = logging.getLogger(__name__)


class SenseiDashboard(TemplateView):
    template_name = "pages/sensei_dashboard.html"

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)


class StudentDashboard(TemplateView):
    template_name = "pages/student_dashboard.html"

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)
