import base64
from datetime import datetime, timezone, timedelta
from io import BytesIO
from secrets import token_urlsafe

import qrcode
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ValidationError
from django.core.management import call_command
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse, reverse_lazy
from django.views.generic import TemplateView
import logging

from dashboard.models import Training, Dojo, Technique, TechniqueCategory, TrainingStatus, KataSerie, Kata, KataLesson
from dojo.mixins.view_mixins import AdminRequiredMixin
from user_management.models import User, Token, Category, TokenType
from user_management.forms import UserUpdateForm

logger = logging.getLogger(__name__)


class SenseiDashboard(LoginRequiredMixin, AdminRequiredMixin, TemplateView):
    template_name = "dashboard/sensei/dashboard.html"

    def get(self, request, *args, **kwargs):
        user_cat = request.user.category
        if user_cat != Category.SENSEI:
            return redirect('student_dashboard')
        trainings = Training.objects.all().order_by('-date')[:6]
        ctx = {
            "trainings": trainings,
        }
        return render(request, self.template_name, ctx)


class ManageTrainings(LoginRequiredMixin, AdminRequiredMixin, TemplateView):
    template_name = "dashboard/sensei/manage_trainings.html"

    def get(self, request, *args, **kwargs):
        trainings = Training.objects.all()
        now = datetime.now(timezone.utc)
        for t in trainings:
            if now > t.date + timedelta(hours=2) and t.status:
                t.status = TrainingStatus.FINALIZADO
                if t.qr_image:
                    t.qr_image.delete(save=False)
                    t.qr_image = None
                t.training_code = ''
                t.save()
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
            training_status = request.POST.get('training_status')
            if training_status not in [TrainingStatus.AGENDADO, TrainingStatus.FINALIZADO, TrainingStatus.CANCELADO]:
                raise ValidationError("Invalid training status value.")

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
            return JsonResponse({'errors': str(e)}, status=400)
        except Technique.DoesNotExist:
            return JsonResponse({'errors': 'One or more selected techniques do not exist.'}, status=400)
        except Exception as e:
            return JsonResponse({'errors': 'An unexpected errors occurred.'}, status=500)

        trainings = Training.objects.filter(status=True)
        techniques = Technique.objects.all()
        ctx = {
            "trainings": trainings,
            "techniques": techniques,
        }
        return render(request, self.template_name, context=ctx)


class ManageTechniques(LoginRequiredMixin, AdminRequiredMixin, TemplateView):
    template_name = "dashboard/sensei/../templates/dashboard/student/learning/manage_techniques.html"

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
                'errors': 'Invalid data submitted.',
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


class ManageStudents(LoginRequiredMixin, AdminRequiredMixin, TemplateView):
    template_name = "dashboard/sensei/manage_students.html"
    ctx = dict()

    def get(self, request, *args, **kwargs):
        call_command('cleanup_expired_tokens', verbosity=0)
        sensei = request.user
        #TODO: how to deal with a sensei with more than one dojo?
        dojo = Dojo.objects.filter(sensei=sensei).first()
        self.ctx['students'] = User.objects.filter(category=Category.ESTUDIANTE) # dojo.students.all() if dojo else []
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
            Token.objects.all().delete()  # Clear existing tokens
            # Create a new token with the provided expiration date
            Token.objects.create(
                token=register_code,
                type=TokenType.SIGNUP,
                created_at=datetime.now(timezone.utc),
                expires_at=expiration_datetime
            )

        elif request.POST.get('_method') == 'delete':
            url = request.POST['url']
            token = url.split('/')[-2]
            Token.objects.filter(token=token).delete()

        self.ctx['time_url'] = [
            (t.expires_at, reverse('signup', kwargs={'token': t.token}))
            for t in Token.objects.all()
        ]

        self.request.session['errors'] = None
        self.request.session['msg'] = "Update successful!"


        return render(request, self.template_name, context=self.ctx)


class ManageProfile(LoginRequiredMixin, AdminRequiredMixin, TemplateView):
    template_name = "dashboard/sensei/manage_profile.html"

    def get(self, request, *args, **kwargs):
        pk = kwargs.get('pk')
        student = get_object_or_404(User, pk=pk)
        form = UserUpdateForm(instance=student)
        qr_code = generate_qr_code(student.id_number)
        ctx = {
            'form': form,
            'student': student,
            'qr_code': f"data:image/png;base64,{qr_code}",
        }
        return render(request, self.template_name, context=ctx)

    def post(self, request, *args, **kwargs):
        pk = kwargs.get('pk')
        student = get_object_or_404(User, pk=pk)

        if request.POST.get('action') == 'switch_status':
            # Handle the switch action
            if student.is_active:
                student.is_active = False
                student.date_deactivated = datetime.now()
                student.date_reactivated = None
                student.save()
                self.request.session['msg'] = "User deactivated successfully!"
            else:
                student.is_active = True
                student.date_reactivated = datetime.now()
                student.date_deactivated = None
                student.save()
                self.request.session['msg'] = "User activated successfully!"
            return redirect('manage_profile', pk=pk)
        elif self.request.POST.get('action') == 'delete':
            student.delete()
            self.request.session['msg'] = "User deleted successfully!"
            return redirect('manage_students')
        elif self.request.FILES.get('picture'):
            # Handle picture upload
            if student.picture:
                student.picture.delete(save=False)

            uploaded_file = self.request.FILES['picture']
            ext = uploaded_file.name.rsplit('.')[-1]
            student.picture.save(f'{pk}.{ext}', self.request.FILES['picture'], save=True)
            form = UserUpdateForm(self.request.POST, self.request.FILES, instance=student)
            ctx = {
                'form': form,
                'student': student,
            }
            return render(request, self.template_name, context=ctx)
        else:
            form = UserUpdateForm(request.POST, instance=student)

            if form.is_valid():
                return self.form_valid(form)
            else:
                return  self.form_invalid(form, student, request)

    def form_valid(self, form):
        # Process the form
        updated_user = form.save()
        self.request.session['errors'] = None
        self.request.session['msg'] = "Update successful!"
        return redirect('manage_profile', pk=updated_user.pk)

    def form_invalid(self, form, student, request):
        request.session['errors'] = form.errors
        request.session['msg'] = "Update failed!"
        ctx = {
            'form': form,
            'student': student,
        }
        return self.render_to_response(self.get_context_data(form=form))


######################################### STUDENT VIEWS #########################################


class StudentDashboard(LoginRequiredMixin, TemplateView):
    template_name = "dashboard/student/dashboard.html"

    def get(self, request, *args, **kwargs):
        trainings = Training.objects.all().order_by('-date')[:6]
        pk = request.user.pk
        student = get_object_or_404(User, pk=pk)
        ctx = {
            "trainings": trainings,
            "student": student,
            "techniques": Technique.objects.all(),
        }
        return render(request, self.template_name, ctx)


class StudentProfile(LoginRequiredMixin, TemplateView):
    template_name = "dashboard/student/profile.html"

    def get(self, request, *args, **kwargs):
        pk = request.user.pk
        student = get_object_or_404(User, pk=pk)
        form = UserUpdateForm(instance=student)
        qr_code = generate_qr_code(student.id_number)
        ctx = {
            'form': form,
            'student': student,
            'qr_code': f"data:image/png;base64,{qr_code}",
        }
        return render(request, self.template_name, context=ctx)

    def post(self, request, *args, **kwargs):
        pk = request.user.pk
        student = get_object_or_404(User, pk=pk)
        form = UserUpdateForm(request.POST, request.FILES, instance=student)
        if request.FILES.get('picture'):
            if student.picture:
                student.picture.delete(save=False)

            uploaded_file = request.FILES['picture']
            ext = uploaded_file.name.rsplit('.')[-1]
            student.picture.save(f'{pk}.{ext}', request.FILES['picture'], save=True)
            ctx = {
                'form': form,
                'student': student,
            }
            return render(request, self.template_name, context=ctx)
        if form.is_valid():
            return self.form_invalid(form, request)
            # return self.form_valid(form)
        else:
            return self.form_invalid(form, request)
            # return render(request, self.template_name, context=ctx)

    def form_valid(self, form):
        # Process the form
        form.save()
        self.request.session['errors'] = None
        self.request.session['msg'] = "Update successful!"
        return redirect('profile')

    def form_invalid(self, form, request):
        request.session['errors'] = form.errors
        request.session['msg'] = "Update failed!"
        # ctx = {
        #     'form': form,
        #     'student': student,
        # }
        return redirect('profile')


def generate_qr_code(data):
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=3,
    )
    qr.add_data(data)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")
    buffered = BytesIO()
    img.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode('utf-8')
    return img_str


class Library(TemplateView):
    template_name = "dashboard/student/learning/library.html"

    def get(self, request, *args, **kwargs):
        series = KataSerie.objects.all()
        techniques = Technique.objects.all()
        ctx = {
            'series': series,
            'techniques': techniques,
        }
        return render(request, self.template_name, context=ctx)


class Techniques(TemplateView):
    template_name = "dashboard/student/learning/techniques.html"

    def get(self, request, *args, **kwargs):
        techniques = Technique.objects.all()
        return render(request, self.template_name, context={'techniques': techniques})


class KataSeries(TemplateView):
    template_name = "dashboard/student/learning/kata_series.html"

    def get(self, request, *args, **kwargs):
        series = KataSerie.objects.all()
        return render(request, self.template_name, context={'series': series})


class KataDetail(TemplateView):
    template_name = "dashboard/student/learning/kata_detail.html"

    def get(self, request, *args, **kwargs):
        pk = kwargs.get('pk')
        kata = get_object_or_404(Kata, pk=pk)
        ctx = {
            'kata': kata,
        }
        return render(request, self.template_name, context=ctx)


class KataLessonDetail(TemplateView):
    template_name = "dashboard/student/learning/kata_lesson_detail.html"

    def get(self, request, *args, **kwargs):
        pk = kwargs.get('pk')
        lesson = get_object_or_404(KataLesson, pk=pk)
        ctx = {
            'lesson': lesson,
        }
        return render(request, self.template_name, context=ctx)
