from datetime import datetime, timedelta
from secrets import token_urlsafe

from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.management import call_command
from django.shortcuts import render
from django.urls import reverse
from django.views.generic import TemplateView
import logging

from dashboard.models import Training, Dojo, Technique, TechniqueCategory
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
        trainings = Training.objects.filter(status=True)
        techniques = Technique.objects.all()
        ctx = {
            "trainings": trainings,
            "techniques": techniques,
        }
        return render(request, self.template_name, context=ctx)

    def post(self, request, *args, **kwargs):
        train = Training(
            date=request.POST['training_date'],
            status=request.POST['training_status'],
        )
        for t_id in request.POST['techniques']:
            technique = Technique.objects.get(pk=t_id)
            train.techniques.add(technique)
        train.save()

        trainings = Training.objects.filter(status=True)
        techniques = Technique.objects.all()
        ctx = {
            "trainings": trainings,
            "techniques": techniques,
        }
        return render(request, self.template_name, context=ctx)


class ManageTechniquesView(LoginRequiredMixin, UserCategoryRequiredMixin, TemplateView):
    template_name = "pages/sensei/manage_techniques.html"

    def get(self, request, *args, **kwargs):
        techniques = Technique.objects.all()
        categories = TechniqueCategory.choices
        ctx = {
            "techniques": techniques,
            "categories": categories,
        }
        return render(request, self.template_name, context=ctx)

    def post(self, request, *args, **kwargs):
        name = request.POST.get('technique_name')
        image = request.FILES.get('technique_image')
        category = request.POST.get('technique_category')
        if not name or category not in dict(TechniqueCategory.choices):
            return render(request, self.template_name, {
                'error': 'Invalid data submitted.',
                'technique_categories': TechniqueCategory.choices
            })

        Technique.objects.create(
            name=name,
            image=image,
            category=category,
        )

        techniques = Technique.objects.all()
        categories = TechniqueCategory.choices
        ctx = {
            "techniques": techniques,
            "categories": categories,
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
