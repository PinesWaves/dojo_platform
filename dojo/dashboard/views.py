from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.views.generic import TemplateView
import logging

logger = logging.getLogger(__name__)


class SenseiDashboard(LoginRequiredMixin, TemplateView):
    template_name = "pages/sensei_dashboard.html"

    def get(self, request, *args, **kwargs):

        return render(request, self.template_name)


class StudentDashboard(LoginRequiredMixin, TemplateView):
    template_name = "pages/student_dashboard.html"

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)
