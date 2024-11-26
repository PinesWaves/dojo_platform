import hashlib
from datetime import datetime, timedelta
from secrets import token_urlsafe

import bcrypt
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.urls import reverse
from django.views.generic import TemplateView
import logging

from dashboard.models import Training, Dojo
from dojo.mixins.view_mixins import UserCategoryRequiredMixin
from user_management.models import User, Token

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
        self.ctx['time_url'] = [
            (t.expires_at, reverse('signup', kwargs={'token': t.token}))
            for t in Token.objects.all()
        ]
        return render(request, self.template_name, context=self.ctx)

    def post(self, request, *args, **kwargs):
        if expiration_datetime := request.POST['expiration_datetime']:
            expiration_datetime = datetime.strptime(expiration_datetime, '%m/%d/%Y %I:%M %p')
            register_code = token_urlsafe(30)

            # Save the token to the database
            Token.objects.create(
                token=register_code,
                expires_at=expiration_datetime
            )

            register_url = reverse('signup', kwargs={'token': register_code})
            self.ctx['time_url'] = register_url
        else:
            self.ctx['time_url'] = ''

        return render(request, self.template_name, context=self.ctx)
