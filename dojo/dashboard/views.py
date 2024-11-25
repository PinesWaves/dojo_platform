import hashlib
from datetime import datetime
import bcrypt
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.urls import reverse
from django.views.generic import TemplateView
import logging

from dashboard.models import Training, Dojo
from dojo.mixins.view_mixins import UserCategoryRequiredMixin
from user_management.models import User

logger = logging.getLogger(__name__)


class SenseiDashboard(LoginRequiredMixin, UserCategoryRequiredMixin, TemplateView):
    template_name = "pages/sensei/dashboard.html"

    def get(self, request, *args, **kwargs):

        return render(request, self.template_name)


class StudentDashboard(LoginRequiredMixin, TemplateView):
    template_name = "pages/student/dashboard.html"

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)


class ManageTrainingsView(LoginRequiredMixin, UserCategoryRequiredMixin, TemplateView):
    template_name = "pages/sensei/manage_trainings.html"

    def get(self, request, *args, **kwargs):
        trainings = Training.objects.all()
        ctx = {
            "trainings": trainings,
        }
        return render(request, self.template_name, context=ctx)


class ManageStudentsView(LoginRequiredMixin, UserCategoryRequiredMixin, TemplateView):
    template_name = "pages/sensei/manage_students.html"
    ctx = dict()

    def get(self, request, *args, **kwargs):
        sensei = request.user
        dojo = Dojo.objects.filter(sensei=sensei)
        self.ctx['students'] = dojo.students if dojo else []
        self.ctx['reg_url'] = ''
        return render(request, self.template_name, context=self.ctx)

    def post(self, request, *args, **kwargs):
        if request.POST['reg_time']:
            reg_time = request.POST['reg_time']
            salt = bcrypt.gensalt()
            hashed = bcrypt.hashpw(datetime.now().strftime('%Y%m%d%H%M%S'), salt)
            register_code = hashlib.sha256(hashed.encode()).hexdigest()[:10]
            register_url = reverse('signup', kwargs={'token': register_code})
            self.ctx['reg_url'] = register_url
        else:
            self.ctx['reg_url'] = ''
        breakpoint()

        return render(request, self.template_name, context=self.ctx)
