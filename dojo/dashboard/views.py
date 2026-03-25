import calendar
from collections import defaultdict
from datetime import date, datetime, timedelta
from secrets import token_urlsafe
import json
import logging

from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ValidationError
from django.core.management import call_command
from django.db import transaction
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.http import require_POST
from django.views.generic import TemplateView

from dashboard.forms import TrainingSchedulingForm, TrainingForm
from dashboard.models import Training, Dojo, Technique, TrainingStatus, KataSerie, Kata, KataLesson, \
    KataLessonActivity, TrainingScheduling, ActivityCompletion, LessonCompletion, Attendance, AttendanceStatus
from dojo.mixins.view_mixins import AdminRequiredMixin
from user_management.models import User, Token, Category, TokenType, UserDocument
from user_management.forms import UserUpdateForm, UploadDocumentsForm, CustomPasswordChangeForm
from utils.config_vars import Ranges
from utils.utils import get_qr_base64, get_next_closest_day

logger = logging.getLogger(__name__)


class SenseiDashboard(LoginRequiredMixin, AdminRequiredMixin, TemplateView):
    template_name = "dashboard/sensei/dashboard.html"

    def get(self, request, *args, **kwargs):
        # from django.db.models import Count, Q, Max
        import json

        user_cat = request.user.category
        if not (user_cat in (Category.SENSEI, Category.SEMPAI)):
            return redirect('student_dashboard')

        today = timezone.now().date()
        week_start = today - timedelta(days=today.weekday())
        week_end = week_start + timedelta(days=6)

        # Get trainings for the training list
        trainings = Training.objects.prefetch_related(
            'attendances', 'techniques'
        ).filter(
            date__range=(
                today - timedelta(days=1),
                today + timedelta(days=6)
            )
        ).order_by('date')

        # Stats calculations
        total_students = User.objects.filter(category=Category.STUDENT).count()
        active_students = User.objects.filter(category=Category.STUDENT, is_active=True)
        trainings_this_week = Training.objects.filter(
            date__range=(week_start, week_end)
        ).count()

        # Calculate attendance rate
        from dashboard.models import Attendance
        total_attendances = Attendance.objects.count()
        total_trainings_held = Training.objects.filter(status=TrainingStatus.FINISHED).count()
        if total_students > 0 and total_trainings_held > 0:
            attendance_rate = (total_attendances / (total_students * total_trainings_held)) * 100
        else:
            attendance_rate = 0

        # Belt distribution
        belt_labels, belt_colors, belt_counts = [], [], []
        for i, r in enumerate(Ranges):
            count = active_students.filter(level=r.value).count()
            if count > 0:
                belt_labels.append(r.label)
                belt_colors.append(r.belt_color)
                belt_counts.append(count)

        # Low attendance students (less than 50%)
        low_attendance_students = []
        for student in active_students[:10]:
            student_attendances = Attendance.objects.filter(student=student).count()
            if total_trainings_held > 0:
                student.attendance_percentage = (student_attendances / total_trainings_held) * 100
            else:
                student.attendance_percentage = 0
            if student.attendance_percentage < 50 and student.attendance_percentage > 0:
                low_attendance_students.append(student)

        # Upcoming trainings
        upcoming_trainings = Training.objects.prefetch_related('attendances').filter(
            date__gte=today
        ).order_by('date')[:5]

        # Recent students with activity
        recent_students = []
        for student in active_students.order_by('-date_joined')[:10]:
            student_attendances = Attendance.objects.filter(student=student)
            student.total_attendances = student_attendances.count()
            if total_trainings_held > 0:
                student.attendance_percentage = (student.total_attendances / total_trainings_held) * 100
            else:
                student.attendance_percentage = 0
            last_attendance = student_attendances.order_by('-training__date').first()
            student.last_attendance = last_attendance.training.date if last_attendance else None
            recent_students.append(student)

        # Student progress on kata lessons
        lessons = KataLesson.objects.prefetch_related('activities').all()
        total_lessons = lessons.count()
        total_available_activities = sum(lesson.activities.count() for lesson in lessons)

        # Calculate progress for all students
        student_progress_list = []
        for student in active_students:
            completed_activities_count = ActivityCompletion.objects.filter(student=student).count()
            completed_lessons_count = LessonCompletion.objects.filter(student=student).count()

            progress_percentage = 0
            if total_available_activities > 0:
                progress_percentage = (completed_activities_count / total_available_activities) * 100

            student_progress_list.append({
                'student': student,
                'completed_lessons': completed_lessons_count,
                'completed_activities': completed_activities_count,
                'progress_percentage': round(progress_percentage, 1),
            })

        # Sort by progress and get top 5
        top_students = sorted(student_progress_list, key=lambda x: x['progress_percentage'], reverse=True)[:5]

        # Calculate overall completion stats
        total_lesson_completions = LessonCompletion.objects.count()
        total_activity_completions = ActivityCompletion.objects.count()

        ctx = {
            "trainings": trainings,
            "total_students": total_students,
            "active_students": active_students.count(),
            "trainings_this_week": trainings_this_week,
            "attendance_rate": attendance_rate,
            "belt_labels": json.dumps(belt_labels),
            "belt_colors": json.dumps(belt_colors),
            "belt_data": json.dumps(belt_counts),
            "low_attendance_students": low_attendance_students[:5],
            "upcoming_trainings": upcoming_trainings,
            "recent_students": recent_students,
            # Student progress data
            "top_students_progress": top_students,
            "total_lessons": total_lessons,
            "total_lesson_completions": total_lesson_completions,
            "total_activity_completions": total_activity_completions,
        }
        return render(request, self.template_name, ctx)


class ManageTrainings(LoginRequiredMixin, AdminRequiredMixin, TemplateView):
    template_name = "dashboard/sensei/manage_trainings.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        trainings = Training.objects.prefetch_related(
            'attendances', 'techniques'
        ).filter(
            date__lte=timezone.now() + timedelta(days=30)
        ).order_by('-date')
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

        elif training_id := request.POST.get('finish_training'):
            try:
                training = Training.objects.get(id=training_id)
                training.status = TrainingStatus.FINISHED
                training.save(update_fields=['status'])
                self.request.session['msg'] = "Training marked as finished!"
            except Training.DoesNotExist:
                self.request.session['errors'] = "Training not found."
                self.request.session['msg'] = "Failed to finish training!"

        elif training_id := request.POST.get('cancel_training'):
            try:
                training = Training.objects.get(id=training_id)
                training.status = TrainingStatus.CANCELED
                training.save(update_fields=['status'])
                self.request.session['msg'] = "Training canceled!"
            except Training.DoesNotExist:
                self.request.session['errors'] = "Training not found."
                self.request.session['msg'] = "Failed to cancel training!"

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
        password_form = CustomPasswordChangeForm(user=student, request_user=request.user)
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
                student.picture.storage.delete(student.picture.name)

            uploaded_file = self.request.FILES['picture']
            student.picture.save(f'{student.id_number}.png', uploaded_file, save=True)
            form = UserUpdateForm(self.request.POST, self.request.FILES, instance=student, request=request)
            ctx = {
                'form': form,
                'student': student,
            }
            return render(request, self.template_name, context=ctx)
        elif self.request.POST.get('action') == 'docs':
            docs_form = UploadDocumentsForm(request.POST, request.FILES)
            if docs_form.is_valid():
                docs = docs_form.save_documents(user=student)
                messages.success(request, f"{len(docs)} document(s) uploaded successfully!")
                return redirect('manage_profile', pk=pk)
            else:
                messages.error(request, "Please select at least one file and fill in the required fields.")
                return redirect('manage_profile', pk=pk)

        elif self.request.POST.get('action') == 'delete_doc':
            doc_id = request.POST.get('doc_id')
            try:
                doc = UserDocument.objects.get(id=doc_id, user=student)
                doc.file.delete(save=False)  # Delete the file from storage
                doc.delete()  # Delete the database record
                messages.success(request, "Document deleted successfully!")
            except UserDocument.DoesNotExist:
                messages.error(request, "Document not found.")
            return redirect('manage_profile', pk=pk)
        elif self.request.POST.get('action') == 'change_password':
            password_form = CustomPasswordChangeForm(user=student, data=request.POST, request_user=request.user)
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
        request.session['msg'] = "Update failed!"
        docs_form = UploadDocumentsForm()
        password_form = CustomPasswordChangeForm(user=student, request_user=request.user)
        qr_code = get_qr_base64(student.id_number)
        ctx = {
            'form': form,
            'docs_form': docs_form,
            'password_form': password_form,
            'student': student,
            'qr_code': qr_code,
        }
        return render(request, self.template_name, context=ctx)


class StudentDashboard(LoginRequiredMixin, TemplateView):
    template_name = "dashboard/student/dashboard.html"

    def get(self, request, *args, **kwargs):
        from dashboard.models import Attendance
        pk = request.user.pk
        student = get_object_or_404(User, pk=pk)
        today = timezone.now().date()

        # Student's attendance records
        student_attendances = Attendance.objects.filter(student=student).order_by('-training__date')
        total_trainings = student_attendances.count()

        # Calculate attendance rate
        total_trainings_held = Training.objects.filter(status=TrainingStatus.FINISHED).count()
        if total_trainings_held > 0:
            attendance_rate = (total_trainings / total_trainings_held) * 100
        else:
            attendance_rate = 0

        # Training streak calculation
        training_streak = 0
        if student_attendances.exists():
            last_training_date = student_attendances.first().training.date
            current_date = last_training_date
            for attendance in student_attendances:
                if (current_date - attendance.training.date).days <= 7:
                    training_streak += 1
                    current_date = attendance.training.date
                else:
                    break

        # Days in dojo
        # days_in_dojo = (today - student.date_joined.date()).days
        joined = student.date_joined
        joined_date = joined.date() if isinstance(joined, datetime) else joined
        days_in_dojo = (today - joined_date).days

        # Belt progress (simple calculation based on attendance)
        belt_levels = [x.value for x in Ranges]
        current_belt_index = belt_levels.index(student.level) if student.level in belt_levels else 0
        if current_belt_index < len(belt_levels) - 1:
            next_belt = belt_levels[current_belt_index + 1]
            # Simple progress: 10 trainings per belt level
            trainings_for_next_belt = (current_belt_index + 1) * 10
            belt_progress = min((total_trainings / trainings_for_next_belt) * 100, 100)
        else:
            next_belt = "BLACK (Mastery)"
            belt_progress = 100

        # Next training
        next_training = Training.objects.filter(date__gte=timezone.now()).order_by('date').first()

        # Attendance calendar (last 30 days)
        attendance_calendar = []
        for i in range(30):
            date = today - timedelta(days=(29 - i))
            training_on_date = Training.objects.filter(date__date=date).first()
            if training_on_date:
                attended = Attendance.objects.filter(student=student, training=training_on_date).exists()
                if attended:
                    status = 'attended'
                elif training_on_date.date < timezone.now():
                    status = 'missed'
                else:
                    status = 'upcoming'
            else:
                status = ''
            if status:
                attendance_calendar.append({
                    'date': date,
                    'status': status
                })

        qr_code = get_qr_base64(student.id_number)
        ctx = {
            "student": student,
            "total_trainings": total_trainings,
            "attendance_rate": attendance_rate,
            "training_streak": training_streak,
            "days_in_dojo": days_in_dojo,
            "belt_progress": belt_progress,
            "next_belt": next_belt,
            "next_training": next_training,
            "attendance_calendar": attendance_calendar,
            "qr_code": qr_code,
        }
        return render(request, self.template_name, ctx)


class StudentProfile(LoginRequiredMixin, TemplateView):
    template_name = "dashboard/student/profile.html"

    def get(self, request, *args, **kwargs):
        student = request.user
        form = UserUpdateForm(instance=student, request=request)
        docs_form = UploadDocumentsForm()
        password_form = CustomPasswordChangeForm(user=student, request_user=request.user)
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

            if student.picture:
                student.picture.storage.delete(student.picture.name)

            student.picture.save(f'{student.id_number}.png', uploaded_file, save=True)

            messages.success(request, "Picture updated correctly.")
            return redirect('profile')

        elif request.POST.get('action') == 'change_password':
            password_form = CustomPasswordChangeForm(user=student, data=request.POST, request_user=request.user)
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

        elif request.POST.get('action') == 'docs':
            docs_form = UploadDocumentsForm(request.POST, request.FILES)
            if docs_form.is_valid():
                docs = docs_form.save_documents(user=student)
                messages.success(request, f"{len(docs)} document(s) uploaded successfully!")
                return redirect('profile')
            else:
                messages.error(request, "Please select at least one file and fill in the required fields.")
                return redirect('profile')

        elif request.POST.get('action') == 'delete_doc':
            doc_id = request.POST.get('doc_id')
            try:
                doc = UserDocument.objects.get(id=doc_id, user=student)
                doc.file.delete(save=False)  # Delete the file from storage
                doc.delete()  # Delete the database record
                messages.success(request, "Document deleted successfully!")
            except UserDocument.DoesNotExist:
                messages.error(request, "Document not found.")
            return redirect('profile')

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
        password_form = CustomPasswordChangeForm(user=self.request.user, request_user=self.request.user)
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
    # TODO: colocar info basica de karate
    # TODO: Agregar glosarios
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
        lesson = get_object_or_404(
            KataLesson.objects.prefetch_related(
                'activities__completions',
                'activities__images',
                'activities__videos',
                'completions'
            ),
            pk=pk
        )

        ctx = {
            'lesson': lesson,
        }

        if request.user.is_authenticated:
            student = get_object_or_404(User, pk=request.user.pk)
            ctx['student'] = student

            # Get completion status for each activity
            activity_completion_map = {}
            if student.category == Category.STUDENT:
                completed_activity_ids = ActivityCompletion.objects.filter(
                    student=student,
                    activity__lesson=lesson
                ).values_list('activity_id', flat=True)

                activity_completion_map = {aid: True for aid in completed_activity_ids}

                # Calculate progress
                total_activities = lesson.activities.count()
                completed_activities = len(completed_activity_ids)

                ctx['total_activities'] = total_activities
                ctx['completed_activities'] = completed_activities
                ctx['activity_completion_map'] = activity_completion_map
                ctx['lesson_completed'] = LessonCompletion.objects.filter(
                    student=student,
                    lesson=lesson
                ).exists()

        return render(request, self.template_name, context=ctx)


class TrainingCalendar(LoginRequiredMixin, AdminRequiredMixin, TemplateView):
    """
    Calendar view showing all training sessions (Sensei/Admin only)
    """
    template_name = "dashboard/sensei/calendar.html"

    def get(self, request, *args, **kwargs):
        ctx = {
        }
        return render(request, self.template_name, context=ctx)


class TrainingAttendance(LoginRequiredMixin, AdminRequiredMixin, TemplateView):
    """
    Calendar view showing all training sessions (Sensei/Admin only)
    """
    template_name = "dashboard/sensei/attendance.html"

    @staticmethod
    def month_days(year, month) -> list[tuple[int, str]]:
        _, day_num = calendar.monthrange(year, month)

        # Nombres de los días en español
        # day_name = ['mo', 'tu', 'we', 'th', 'fr', 'sa', 'su']
        day_name = ['l', 'm', 'x', 'j', 'v', 's', 'd']

        # Generar lista de tuplas (día, nombre_día)
        days = [
            (day, day_name[date(year, month, day).weekday()])
            for day in range(1, day_num + 1)
        ]

        return days

    def get(self, request, *args, **kwargs):
        students = User.objects.filter(category=Category.STUDENT, is_active=True).order_by('last_name', 'first_name')
        month_queried = request.GET.get('month')
        if month_queried:
            try:
                month_date = datetime.strptime(month_queried, '%Y-%m')
                year = month_date.year
                month = month_date.month
            except ValueError:
                now = timezone.now()
                year, month = now.year, now.month
        else:
            now = timezone.now()
            year, month = now.year, now.month

        # Trainings in the selected month (filter using local timezone so late-night
        # trainings in Bogota that cross into the next UTC day are counted correctly)
        import calendar as _cal
        local_start = timezone.make_aware(datetime(year, month, 1))
        last_day = _cal.monthrange(year, month)[1]
        local_end = timezone.make_aware(datetime(year, month, last_day, 23, 59, 59))
        trainings = Training.objects.filter(date__range=(local_start, local_end)).order_by('date')
        training_ids = list(trainings.values_list('id', flat=True))

        # Attendance map: {student_id: set(training_id)} — only PRESENT records
        attendance_qs = Attendance.objects.filter(
            training_id__in=training_ids, status__in=(AttendanceStatus.PRESENT, AttendanceStatus.LATE)
        )
        attendance_map = {}
        for att in attendance_qs:
            attendance_map.setdefault(att.student_id, set()).add(att.training_id)

        # Group training IDs by local date (days with multiple sessions count as one)
        training_date_map = defaultdict(list)
        for training in trainings:
            local_date = timezone.localtime(training.date).date()
            training_date_map[local_date].append(training.id)
        total_unique_days = len(training_date_map)

        # Build student rows
        student_rows = []
        for student in students:
            attended_ids = attendance_map.get(student.id, set())
            # A day is attended if the student attended at least one session that day
            days_attended = sum(
                1 for day_ids in training_date_map.values()
                if any(tid in attended_ids for tid in day_ids)
            )
            student_rows.append({
                'student': student,
                'attended_ids': list(attended_ids),
                't_attend': days_attended,
                't_missed': total_unique_days - days_attended,
            })

        # Pagination: all 12 months of the selected year
        month_abbrs = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                       'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        pagination_months = [
            {
                'num': m,
                'name': month_abbrs[m - 1],
                'year': year,
                'active': m == month,
            }
            for m in range(1, 13)
        ]

        ctx = {
            "year": year,
            "month": month,
            "trainings": trainings,
            "student_rows": student_rows,
            "pagination_months": pagination_months,
            "prev_year": year - 1,
            "next_year": year + 1,
        }
        return render(request, self.template_name, context=ctx)


@require_POST
def toggle_attendance(request):
    """
    AJAX endpoint to toggle a student's attendance for a training session.

    Request (POST JSON):
    {
        "training_id": 1,
        "student_id": 2
    }

    Response:
    {
        "status": "created" | "deleted",
        "attendance_id": 5  (only when created)
    }
    """
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Authentication required'}, status=401)

    try:
        data = json.loads(request.body)
        training_id = data.get('training_id')
        student_id = data.get('student_id')
    except (json.JSONDecodeError, ValueError):
        return JsonResponse({'error': 'Invalid JSON'}, status=400)

    if not training_id or not student_id:
        return JsonResponse({'error': 'training_id and student_id are required'}, status=400)

    training = get_object_or_404(Training, pk=training_id)
    student = get_object_or_404(User, pk=student_id, category=Category.STUDENT)

    attendance = Attendance.objects.filter(training=training, student=student).first()
    if attendance:
        if attendance.status == AttendanceStatus.PRESENT:
            attendance.delete()
            return JsonResponse({'status': 'deleted'})
        else:
            attendance.status = AttendanceStatus.PRESENT
            attendance.save()
            return JsonResponse({'status': 'created', 'attendance_id': attendance.id})

    attendance = Attendance.objects.create(
        training=training,
        student=student,
        status=AttendanceStatus.PRESENT,
    )
    return JsonResponse({'status': 'created', 'attendance_id': attendance.id})


@require_POST
def register_qr_attendance(request):
    """
    Register attendance via QR code scan.
    The QR code must encode the student's id_number.
    Finds today's training that is ongoing or starting within 30 minutes.
    """
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Authentication required'}, status=401)

    try:
        data = json.loads(request.body)
        qr_data = str(data.get('qr_data', '')).strip()
    except (json.JSONDecodeError, ValueError):
        return JsonResponse({'error': 'Invalid JSON'}, status=400)

    if not qr_data:
        return JsonResponse({'error': 'QR data is required'}, status=400)

    student = User.objects.filter(
        id_number=qr_data, category=Category.STUDENT, is_active=True
    ).first()
    if not student:
        return JsonResponse({'error': 'Student not found'}, status=404)

    now = timezone.now()
    training = Training.objects.filter(
        date__range=(now - timedelta(minutes=90), now + timedelta(minutes=30)),
    ).exclude(status=TrainingStatus.CANCELED).order_by('-date').first()

    if not training:
        return JsonResponse({'error': f'Hi {student}.<br>No active or upcoming training found for today'}, status=404)

    attendance, created = Attendance.objects.get_or_create(
        training=training,
        student=student,
        defaults={'status': AttendanceStatus.PRESENT},
    )
    if not created and attendance.status != AttendanceStatus.PRESENT:
        attendance.status = AttendanceStatus.PRESENT
        attendance.save()
        created = True

    return JsonResponse({
        'status': 'created' if created else 'already',
        'student_name': f'{student.first_name} {student.last_name}',
        'training_id': training.id,
        'student_id': student.id,
    })


class StudentCalendar(LoginRequiredMixin, TemplateView):
    """
    Calendar view for students showing all training sessions
    """
    template_name = "dashboard/student/calendar.html"

    def get(self, request, *args, **kwargs):
        pk = request.user.pk
        student = get_object_or_404(User, pk=pk)
        ctx = {
            'student': student,
        }
        return render(request, self.template_name, context=ctx)


class StudentProgressView(LoginRequiredMixin, AdminRequiredMixin, TemplateView):
    """
    Sensei dashboard view for viewing all student progress on kata lessons.
    Shows completion statistics and detailed progress per student.
    """
    template_name = "dashboard/sensei/student_progress.html"

    def get(self, request, *args, **kwargs):
        # Get all students
        students = User.objects.filter(category=Category.STUDENT).order_by('first_name', 'last_name')

        # Get all lessons for reference
        lessons = KataLesson.objects.prefetch_related('kata', 'activities').order_by('kata__order', 'order')

        # Build progress data structure
        student_progress_data = []
        for student in students:
            # Get all completed activities by this student
            completed_activities = ActivityCompletion.objects.filter(
                student=student
            ).select_related('activity__lesson__kata')

            # Get all completed lessons
            completed_lessons = LessonCompletion.objects.filter(
                student=student
            ).select_related('lesson__kata')

            total_lessons_completed = completed_lessons.count()
            total_activities_completed = completed_activities.count()

            # Calculate total available activities across all lessons
            total_available_activities = sum(lesson.activities.count() for lesson in lessons)

            # Progress percentage
            progress_percentage = 0
            if total_available_activities > 0:
                progress_percentage = (total_activities_completed / total_available_activities) * 100

            student_progress_data.append({
                'student': student,
                'total_lessons_completed': total_lessons_completed,
                'total_activities_completed': total_activities_completed,
                'progress_percentage': round(progress_percentage, 1),
                'completed_lesson_ids': [cl.lesson.id for cl in completed_lessons],
            })

        ctx = {
            'student_progress_data': student_progress_data,
            'lessons': lessons,
            'total_lessons': lessons.count(),
        }

        return render(request, self.template_name, context=ctx)


class StudentProgressDetail(LoginRequiredMixin, AdminRequiredMixin, TemplateView):
    """
    Detailed view of a specific student's progress on all kata lessons.
    """
    template_name = "dashboard/sensei/student_progress_detail.html"

    def get(self, request, *args, **kwargs):
        student_id = kwargs.get('student_id')
        student = get_object_or_404(User, pk=student_id, category=Category.STUDENT)

        # Get all katas with their lessons
        katas = Kata.objects.prefetch_related('lessons__activities').order_by('order')

        # Build detailed progress data
        kata_progress = []
        for kata in katas:
            lessons_data = []
            for lesson in kata.lessons.all():
                total_activities = lesson.activities.count()
                completed_count = ActivityCompletion.objects.filter(
                    student=student,
                    activity__lesson=lesson
                ).count()

                is_lesson_completed = LessonCompletion.objects.filter(
                    student=student,
                    lesson=lesson
                ).exists()

                # Get completed activity IDs
                completed_activity_ids = ActivityCompletion.objects.filter(
                    student=student,
                    activity__lesson=lesson
                ).values_list('activity_id', flat=True)

                lessons_data.append({
                    'lesson': lesson,
                    'total_activities': total_activities,
                    'completed_activities': completed_count,
                    'is_completed': is_lesson_completed,
                    'progress_percentage': (completed_count / total_activities * 100) if total_activities > 0 else 0,
                    'completed_activity_ids': list(completed_activity_ids),
                })

            kata_progress.append({
                'kata': kata,
                'lessons': lessons_data,
            })

        ctx = {
            'student': student,
            'kata_progress': kata_progress,
        }

        return render(request, self.template_name, context=ctx)


def get_trainings_json(request):
    """
    API endpoint to return training data as JSON for the calendar
    """
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Authentication required'}, status=401)

    # Get all trainings
    trainings = Training.objects.prefetch_related('attendances', 'techniques').all()

    # Format trainings for FullCalendar
    events = []
    for training in trainings:
        # Determine background color based on status
        if training.status == TrainingStatus.SCHEDULED:
            bg_color = '#ffc800'  # Yellow for scheduled
        elif training.status == TrainingStatus.ONGOING:
            bg_color = '#3c8dbc'  # Yellow for scheduled
        elif training.status == TrainingStatus.FINISHED:
            bg_color = '#00a65a'  # Green for finished
        elif training.status == TrainingStatus.CANCELED:
            bg_color = '#dd4b39'  # Red for cancelled
        else:
            bg_color = '#3c8dbc'  # Default light blue

        # Count attendances
        attendance_count = training.attendances.filter(status="P").count()

        # Get techniques list
        techniques_list = ', '.join([t.name for t in training.techniques.all()[:3]])
        if training.techniques.count() > 3:
            techniques_list += f' +{training.techniques.count() - 3} more'

        # Build event title
        title = f"({attendance_count} std)"

        # Build description for event
        description = f"Status: {training.get_status_display()}\n"
        description += f"Attendees: {attendance_count}\n"
        if techniques_list:
            description += f"Techniques: {techniques_list}"

        events.append({
            'id': training.id,
            'title': title,
            'start': training.date.isoformat(),
            'backgroundColor': bg_color,
            'borderColor': bg_color,
            'description': description,
            'status': training.status,
            'url': f'/dashboard/manage_trainings/?training_id={training.id}',  # Link to training detail
        })

    return JsonResponse(events, safe=False)


@require_POST
def toggle_activity_completion(request):
    """
    AJAX endpoint to mark/unmark an activity as completed.

    Request (POST JSON):
    {
        "activity_id": 123,
        "completed": true/false
    }

    Response:
    {
        "success": true,
        "completed": true,
        "message": "Activity marked as completed",
        "lesson_completed": false,
        "total_activities": 5,
        "completed_activities": 3
    }
    """
    if not request.user.is_authenticated:
        return JsonResponse({'success': False, 'error': 'Authentication required'}, status=401)

    if request.user.category != Category.STUDENT:
        return JsonResponse({'success': False, 'error': 'Only students can mark activities'}, status=403)

    try:
        data = json.loads(request.body)
        activity_id = data.get('activity_id')
        should_complete = data.get('completed', True)

        if not activity_id:
            return JsonResponse({'success': False, 'error': 'activity_id required'}, status=400)

        activity = get_object_or_404(KataLessonActivity, pk=activity_id)
        student = request.user

        with transaction.atomic():
            if should_complete:
                # Mark as completed
                completion, created = ActivityCompletion.objects.get_or_create(
                    student=student,
                    activity=activity
                )
                message = "Activity marked as completed" if created else "Already completed"
            else:
                # Unmark as completed
                deleted_count = ActivityCompletion.objects.filter(
                    student=student,
                    activity=activity
                ).delete()[0]
                message = "Activity unmarked" if deleted_count > 0 else "Was not completed"

                # Remove lesson completion if it exists
                LessonCompletion.objects.filter(
                    student=student,
                    lesson=activity.lesson
                ).delete()

            # Check if all activities in the lesson are now completed
            lesson = activity.lesson
            total_activities = lesson.activities.count()
            completed_activities = ActivityCompletion.objects.filter(
                student=student,
                activity__lesson=lesson
            ).count()

            lesson_completed = False
            if should_complete and completed_activities == total_activities and total_activities > 0:
                # Auto-create lesson completion
                LessonCompletion.objects.get_or_create(
                    student=student,
                    lesson=lesson
                )
                lesson_completed = True

        return JsonResponse({
            'success': True,
            'completed': should_complete,
            'message': message,
            'lesson_completed': lesson_completed,
            'total_activities': total_activities,
            'completed_activities': completed_activities
        })

    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        logger.error(f"Error toggling activity completion: {str(e)}")
        return JsonResponse({'success': False, 'error': str(e)}, status=500)
