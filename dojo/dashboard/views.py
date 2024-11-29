from datetime import datetime, timedelta
from secrets import token_urlsafe

from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.management import call_command
from django.shortcuts import render
from django.urls import reverse
from django.views.generic import TemplateView
import logging

from dashboard.models import Training, Dojo, Technique
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

    def post(self, request, *args, **kwargs):
        train = Training(
            date=request.POST['date'],
            status=request.POST['status'],
        )
        for t_id in request.POST['techniques']:
            technique = Technique.objects.get(pk=t_id)
            train.techniques.add(technique)
        train.save()

        trainings = Training.objects.all()
        ctx = {
            "trainings": trainings,
        }
        return render(request, self.template_name, context=ctx)



class ManageStudentsView(LoginRequiredMixin, UserCategoryRequiredMixin, TemplateView):
    template_name = "pages/sensei/manage_students.html"
    ctx = dict()

    def get(self, request, *args, **kwargs):
        call_command('cleanup_expired_tokens', verbosity=0)
        sensei = request.user
        dojo = Dojo.objects.filter(sensei=sensei)
        self.ctx['students'] = dojo.students if dojo else []
        self.ctx['time_url'] = [
            (t.expires_at, reverse('signup', kwargs={'token': t.token}))
            for t in Token.objects.all()
        ]
        if not self.ctx['time_url']:
            self.ctx['time_url'] = None
        return render(request, self.template_name, context=self.ctx)

    def post(self, request, *args, **kwargs):
        if expiration_datetime := request.POST.get('expiration_datetime'):
            expiration_datetime = datetime.strptime(expiration_datetime, '%m/%d/%Y %I:%M %p')
            register_code = token_urlsafe(30)

            # Save the token to the database
            Token.objects.create(
                token=register_code,
                expires_at=expiration_datetime
            )

        if request.POST.get('_method') == 'delete':
            url = request.POST['url']
            token = url.split('/')[2]
            Token.objects.filter(token=token).delete()

        self.ctx['time_url'] = [
            (t.expires_at, reverse('signup', kwargs={'token': t.token}))
            for t in Token.objects.all()
        ]


        return render(request, self.template_name, context=self.ctx)
