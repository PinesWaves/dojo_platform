from datetime import datetime, timedelta
from secrets import token_urlsafe

from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ValidationError
from django.core.management import call_command
from django.http import JsonResponse
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
        try:
            training_date = request.POST.get('training_date')
            if not training_date:
                raise ValidationError("Training date is required.")

            try:
                # Ensure date is in the correct format
                training_date = datetime.strptime(training_date, '%m/%d/%Y %I:%M %p')
            except ValueError:
                raise ValidationError("Invalid date format. Use MM/DD/YYYY HH:MM AM/PM.")

            # Validate `training_status`
            training_status = request.POST.get('training_status', 'on')  # Default to 'off' if missing
            if training_status not in ['on', 'off']:
                raise ValidationError("Invalid training status value.")
            training_status = True if training_status == 'on' else False

            training_techniques = request.POST.getlist('training_techniques')

            train = Training(
                date=training_date,
                status=training_status,
            )
            train.save()
            for tc_id in training_techniques:
                technique = Technique.objects.get(pk=tc_id)
                train.techniques.add(technique)
            train.save()
        except ValidationError as e:
            return JsonResponse({'error': str(e)}, status=400)
        except Technique.DoesNotExist:
            return JsonResponse({'error': 'One or more selected techniques do not exist.'}, status=400)
        except Exception as e:
            return JsonResponse({'error': 'An unexpected error occurred.'}, status=500)

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
