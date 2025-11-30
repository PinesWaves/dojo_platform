from datetime import datetime, timedelta
from secrets import token_urlsafe

from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ValidationError
from django.core.management import call_command
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.views.generic import TemplateView
from django.utils import timezone
import logging

from dashboard.forms import TrainingSchedulingForm, TrainingForm
from dashboard.models import Training, Dojo, Technique, TrainingStatus, KataSerie, Kata, KataLesson, \
    TrainingScheduling
from dojo.mixins.view_mixins import AdminRequiredMixin
from user_management.models import User, Token, Category, TokenType, UserDocument
from user_management.forms import UserUpdateForm, UploadDocumentsForm, CustomPasswordChangeForm
from utils.utils import get_qr_base64, get_next_closest_day

logger = logging.getLogger(__name__)


class SenseiDashboard(LoginRequiredMixin, AdminRequiredMixin, TemplateView):
    template_name = "dashboard/sensei/dashboard.html"

    def get(self, request, *args, **kwargs):
        user_cat = request.user.category
        if not (user_cat in (Category.SENSEI, Category.SEMPAI)):
            return redirect('student_dashboard')
        today = timezone.now().date()
        trainings = Training.objects.prefetch_related(
            'attendances', 'techniques'
        ).filter(
            date__range=(
                today - timedelta(days=1),
                today + timedelta(days=6)
            )
        ).order_by('date')
        ctx = {
            "trainings": trainings,
        }
        return render(request, self.template_name, ctx)


class ManageTrainings(LoginRequiredMixin, AdminRequiredMixin, TemplateView):
    template_name = "dashboard/sensei/manage_trainings.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        trainings = Training.objects.prefetch_related('attendances', 'techniques').all()
        training_form = TrainingForm()
        scheduling_form = TrainingSchedulingForm()
        schedules = TrainingScheduling.objects.all()
        context.update({
            "trainings": trainings,
            "training_form": training_form,
            "schedules": schedules,
            "scheduling_form": scheduling_form,
        })
        return context

    def get(self, request, *args, **kwargs):
        now = timezone.now()

        # Efficiently update expired trainings
        trainings_to_update = Training.objects.filter(
            date__lt=now - timedelta(hours=2),
            status=TrainingStatus.SCHEDULED
        )

        trainings_to_update.update(
            status=TrainingStatus.FINISHED,
        )

        ctx = self.get_context_data()
        return render(request, self.template_name, context=ctx)

    def post(self, request, *args, **kwargs):
        if request.POST.get('action') == 'schedule':
            form = TrainingSchedulingForm(request.POST)
            if form.is_valid():
                form.save()
                self.request.session['msg'] = "Schedule created successfully!"
            else:
                self.request.session['errors'] = form.errors
                self.request.session['msg'] = "Failed to create schedule!"

        elif schedule_id := request.POST.get('delete_schedule'):
            try:
                schedule = TrainingScheduling.objects.get(id=schedule_id)
                schedule.delete()
                self.request.session['msg'] = "Schedule deleted successfully!"
            except TrainingScheduling.DoesNotExist:
                self.request.session['errors'] = "Schedule not found."
                self.request.session['msg'] = "Failed to delete schedule!"

        elif request.POST.get('run_scheduling'):
            schedules = TrainingScheduling.objects.all()
            today = timezone.now().date()
            end_of_year = today.replace(month=12, day=31)
            created_count = 0
            for schedule in schedules:
                try:
                    init_date = get_next_closest_day(today, schedule.day_of_week)
                    schedule_dates = []
                    while init_date <= end_of_year:
                        if init_date.weekday() == schedule.day_of_week:
                            schedule_dates.append(
                                timezone.make_aware(datetime.combine(init_date, schedule.time))
                            )
                        init_date += timedelta(days=7)

                    # Filter out dates that already have a training scheduled
                    existing_trainings = Training.objects.filter(
                        date__in=schedule_dates
                    ).values_list('date', flat=True)
                    trainings = [Training(date=d) for d in schedule_dates if d not in existing_trainings]
                    created_count += len(trainings)
                    Training.objects.bulk_create(trainings)

                except ValidationError as e:
                    logger.error(f"Failed to create training from schedule {schedule.id}: {e}")
                    continue  # Skip invalid schedules
                except:
                    breakpoint()

            self.request.session['msg'] = f"{created_count} trainings created from schedules."

        elif request.POST.get('action') == 'new_training':
            # Handle new training creation
            form = TrainingForm(request.POST)
            if form.is_valid():
                form.save()
                self.request.session['errors'] = None
                self.request.session['msg'] = "Training created successfully!"
            else:
                self.request.session['errors'] = form.errors
                self.request.session['msg'] = "Failed to create training!"

        elif request.POST.get('action') == 'update_training':
            training_id = request.POST.get('training_id')
            training = get_object_or_404(Training, id=training_id)
            form = TrainingForm(request.POST, instance=training)
            if form.is_valid():
                form.save()
                self.request.session['errors'] = None
                self.request.session['msg'] = "Training updated successfully!"
            else:
                self.request.session['errors'] = form.errors
                self.request.session['msg'] = "Failed to update training!"

        elif training_id := request.POST.get('delete_training'):
            try:
                training = Training.objects.get(id=training_id)
                training.delete()
                self.request.session['msg'] = "Training deleted successfully!"
            except Training.DoesNotExist:
                self.request.session['errors'] = "Training not found."
                self.request.session['msg'] = "Failed to delete training!"

        ctx = self.get_context_data()
        return render(request, self.template_name, context=ctx)


class ManageTechniques(LoginRequiredMixin, AdminRequiredMixin, TemplateView):
    template_name = "dashboard/sensei/../templates/dashboard/student/learning/manage_techniques.html"

    def get(self, request, *args, **kwargs):
        techniques = Technique.objects.all()
        # categories = TechniqueCategory.choices
        ctx = {
            "techniques": techniques,
            # "categories": categories,
        }
        return render(request, self.template_name, context=ctx)

    def post(self, request, *args, **kwargs):
        name = request.POST.get('technique_name')
        image = request.FILES.get('technique_image')
        category = request.POST.get('technique_category')
        # if not name or category not in dict(TechniqueCategory.choices):
        #     return render(request, self.template_name, {
        #         'errors': 'Invalid data submitted.',
        #         'technique_categories': TechniqueCategory.choices
        #     })

        Technique.objects.create(
            name=name,
            image=image,
            category=category,
        )

        techniques = Technique.objects.all()
        # categories = TechniqueCategory.choices
        ctx = {
            "techniques": techniques,
            # "categories": categories,
        }
        return render(request, self.template_name, context=ctx)


class ManageStudents(LoginRequiredMixin, AdminRequiredMixin, TemplateView):
    template_name = "dashboard/sensei/manage_students.html"
    ctx = dict()

    def get(self, request, *args, **kwargs):
        call_command('cleanup_expired_tokens', verbosity=0)
        sensei = request.user
        #TODO: how to deal with a sensei with more than one dojo?
        dojo = Dojo.objects.prefetch_related('students').filter(sensei=sensei).first()
        self.ctx['students'] = User.objects.filter(category=Category.STUDENT) # dojo.students.all() if dojo else []
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
                created_at=timezone.now(),
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
        form = UserUpdateForm(instance=student, request=request)
        docs_form = UploadDocumentsForm()
        password_form = CustomPasswordChangeForm(user=student)
        qr_code = get_qr_base64(student.id_number)
        ctx = {
            'form': form,
            'docs_form': docs_form,
            'password_form': password_form,
            'student': student,
            'qr_code': qr_code,
        }
        return render(request, self.template_name, context=ctx)

    def post(self, request, *args, **kwargs):
        pk = kwargs.get('pk')
        student = get_object_or_404(User, pk=pk)

        if request.POST.get('action') == 'switch_status':
            # Handle the switch action
            if student.is_active:
                student.is_active = False
                student.date_deactivated = timezone.now()
                student.date_reactivated = None
                student.save()
                self.request.session['msg'] = "User deactivated successfully!"
            else:
                student.is_active = True
                student.date_reactivated = timezone.now()
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
            form = UserUpdateForm(self.request.POST, self.request.FILES, instance=student, request=request)
            ctx = {
                'form': form,
                'student': student,
            }
            return render(request, self.template_name, context=ctx)
        elif self.request.POST.get('action') == 'docs':
            """
            from django.core.files.uploadedfile import InMemoryUploadedFile
    
            # Subir un diploma
            diploma = UserDocument.objects.create(
                user=user_instance,
                document_type=DocumentType.DIPLOMA,
                title="Cinturón Negro 1er Dan JKA",
                description="Diploma otorgado por Sensei César Peña",
                file=uploaded_file
            )
            
            # Subir múltiples documentos
            files = request.FILES.getlist('diplomas')  # En un formulario con multiple=True
            for file in files:
                UserDocument.objects.create(
                    user=request.user,
                    document_type=DocumentType.DIPLOMA,
                    title=file.name,
                    file=file
                )
            """
            form = UploadDocumentsForm(request.POST, request.FILES)
            if form.is_valid():
                files = request.FILES.getlist('files')
                document_type = form.cleaned_data['document_type']
                title = form.cleaned_data['title']

                for file in files:
                    UserDocument.objects.create(
                        user=request.user,
                        document_type=document_type,
                        title=title or file.name,
                        file=file
                    )

                return redirect('profile')
            ctx = {
                'form': form,
                'student': student,
            }
            return render(request, self.template_name, context=ctx)
        elif self.request.POST.get('action') == 'change_password':
            password_form = CustomPasswordChangeForm(user=student, data=request.POST)
            if password_form.is_valid():
                password_form.save()
                # Update session auth hash to prevent logout after password change
                if request.user.pk == student.pk:
                    update_session_auth_hash(request, password_form.user)
                self.request.session['msg'] = "Password changed successfully!"
                return redirect('manage_profile', pk=pk)
            else:
                form = UserUpdateForm(instance=student, request=request)
                docs_form = UploadDocumentsForm()
                qr_code = get_qr_base64(student.id_number)
                self.request.session['errors'] = password_form.errors
                self.request.session['msg'] = "Failed to change password!"
                ctx = {
                    'form': form,
                    'docs_form': docs_form,
                    'password_form': password_form,
                    'student': student,
                    'qr_code': qr_code,
                }
                return render(request, self.template_name, context=ctx)
        else:
            form = UserUpdateForm(request.POST, instance=student, request=request)

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
        trainings = Training.objects.prefetch_related('attendances', 'techniques').order_by('-date')[:6]
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
        student = request.user
        form = UserUpdateForm(instance=student, request=request)
        docs_form = UploadDocumentsForm()
        password_form = CustomPasswordChangeForm(user=student)
        qr_code = get_qr_base64(student.id_number)
        ctx = {
            'form': form,
            'docs_form': docs_form,
            'password_form': password_form,
            'student': student,
            'qr_code': qr_code,
        }
        return render(request, self.template_name, context=ctx)

    def post(self, request, *args, **kwargs):
        student = request.user
        if 'picture' in request.FILES:
            uploaded_file = request.FILES['picture']
            ext = uploaded_file.name.rsplit('.')[-1]

            if student.picture:
                student.picture.delete(save=False)

            student.picture.save(f'{student.pk}.{ext}', uploaded_file, save=True)

            messages.success(request, "Picture updated correctly.")
            return redirect('profile')

        elif request.POST.get('action') == 'change_password':
            password_form = CustomPasswordChangeForm(user=student, data=request.POST)
            if password_form.is_valid():
                password_form.save()
                # Update session auth hash to prevent logout after password change
                update_session_auth_hash(request, password_form.user)
                messages.success(request, "Password changed successfully!")
                return redirect('profile')
            else:
                form = UserUpdateForm(instance=student, request=request)
                docs_form = UploadDocumentsForm()
                qr_code = get_qr_base64(student.id_number)
                context = {
                    'form': form,
                    'docs_form': docs_form,
                    'password_form': password_form,
                    'student': student,
                    'qr_code': qr_code,
                }
                messages.error(request, "There were errors changing the password.")
                return render(request, self.template_name, context)

        form = UserUpdateForm(request.POST, request.FILES, instance=student, request=request)
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def form_valid(self, form):
        form.save()
        messages.success(self.request, "Profile updated correctly.")
        return redirect('profile')

    def form_invalid(self, form):
        qr_code = get_qr_base64(self.request.user.id_number)
        docs_form = UploadDocumentsForm()
        password_form = CustomPasswordChangeForm(user=self.request.user)
        context = {
            'form': form,
            'docs_form': docs_form,
            'password_form': password_form,
            'student': self.request.user,
            'qr_code': qr_code,
        }
        messages.error(self.request, "There were errors updating the profile.")
        return render(self.request, self.template_name, context)


class Library(TemplateView):
    template_name = "dashboard/student/learning/library.html"

    def get(self, request, *args, **kwargs):
        series = KataSerie.objects.prefetch_related('katas').all()
        techniques = Technique.objects.all()
        ctx = {
            'series': series,
            'techniques': techniques,
        }
        if request.user.is_authenticated:
            pk = request.user.pk
            student = get_object_or_404(User, pk=pk)
            ctx['student'] = student

        return render(request, self.template_name, context=ctx)


class Techniques(TemplateView):
    template_name = "dashboard/student/learning/techniques.html"

    def get(self, request, *args, **kwargs):
        techniques = Technique.objects.all()
        ctx = {
            'techniques': techniques,
        }
        if request.user.is_authenticated:
            pk = request.user.pk
            student = get_object_or_404(User, pk=pk)
            ctx['student'] = student

        return render(request, self.template_name, context=ctx)


class KataSeries(TemplateView):
    template_name = "dashboard/student/learning/kata_series.html"

    def get(self, request, *args, **kwargs):
        series = KataSerie.objects.prefetch_related('katas').all()
        ctx = {
            'series': series,
        }
        if request.user.is_authenticated:
            pk = request.user.pk
            student = get_object_or_404(User, pk=pk)
            ctx['student'] = student

        return render(request, self.template_name, context=ctx)


class KataDetail(TemplateView):
    template_name = "dashboard/student/learning/kata_detail.html"

    def get(self, request, *args, **kwargs):
        pk = kwargs.get('pk')
        kata = get_object_or_404(Kata.objects.prefetch_related('lessons'), pk=pk)
        ctx = {
            'current_year': timezone.now().year,
            'kata': kata,
        }
        if request.user.is_authenticated:
            pk = request.user.pk
            student = get_object_or_404(User, pk=pk)
            ctx['student'] = student

        return render(request, self.template_name, context=ctx)


class KataLessonDetail(TemplateView):
    template_name = "dashboard/student/learning/kata_lesson_detail.html"

    def get(self, request, *args, **kwargs):
        pk = kwargs.get('pk')
        lesson = get_object_or_404(KataLesson.objects.prefetch_related('activities'), pk=pk)
        ctx = {
            'current_year': timezone.now().year,
            'lesson': lesson,
        }
        if request.user.is_authenticated:
            pk = request.user.pk
            student = get_object_or_404(User, pk=pk)
            ctx['student'] = student

        return render(request, self.template_name, context=ctx)
