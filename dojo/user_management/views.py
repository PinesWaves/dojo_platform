import logging
from datetime import datetime
from pathlib import Path

import math
from django.contrib import messages
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.contrib.auth.views import LoginView
from django.core.mail import send_mail, EmailMultiAlternatives
from django.template.loader import render_to_string
from django.templatetags.static import static
from django.urls import reverse_lazy, reverse
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.views import View
from django.views.generic import CreateView, UpdateView, DeleteView, TemplateView, FormView
from django.shortcuts import get_object_or_404, render
from django.contrib.auth import get_user_model

from dojo import settings
from .forms import UserRegisterForm, UserUpdateForm, ForgotPassForm, RecoverPassForm
from .models import Category, Token, TokenType

logger = logging.getLogger(__name__)
User = get_user_model()

# Vista de login
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.urls import reverse_lazy
from django.http import HttpResponse


class CustomLoginView(View):
    template_name = 'login_register/login.html'

    def get(self, request):
        user = request.user
        # error = request.session.pop('errors', None)
        # msg = request.session.pop('msg', None)
        if user.is_authenticated:  # Redirige si ya está autenticado
            if user.is_superuser or user.category == Category.SENSEI:
                return redirect(reverse_lazy('sensei_dashboard'))  # Redirigir al dashboard del sensei
            elif user.category == Category.ESTUDIANTE:
                return redirect(reverse_lazy('student_dashboard'))  # Redirigir al dashboard del estudiante
        return render(request, self.template_name) #, {'errors': error, 'msg': msg})

    def post(self, request):
        id_number = request.POST.get('id_number')
        password = request.POST.get('password')

        user = authenticate(request, id_number=id_number, password=password)

        if user:
            if not user.is_active:
                messages.error(request, "Your account is deactivated. Please contact support.")
                return redirect(reverse_lazy('login'))

            # Si las credenciales son válidas, iniciar sesión
            messages.success(request, "Login successful!")

            login(request, user)
            if user.is_superuser or user.category == Category.SENSEI:
                return redirect(reverse_lazy('sensei_dashboard'))
            elif user.category == Category.ESTUDIANTE:
                return redirect(reverse_lazy('student_dashboard'))
            else:
                return redirect(reverse_lazy('login'))

        messages.error(request, "Invalid credentials.")
        return redirect(reverse_lazy('login'))

# Vista de Registro
class RegisterView(FormView):
    model = User
    form_class = UserRegisterForm
    template_name = 'login_register/register.html'
    success_url = reverse_lazy('login')

    def get(self, request, *args, **kwargs):
        token = self.kwargs.get('token')

        # Check if the token exists and is valid
        try:
            registration_token = Token.objects.get(token=token, type=TokenType.SIGNUP)
            if not registration_token.is_valid():
                request.session['errors'] = 'Invalid or expired token'
                return redirect(reverse_lazy('login'))  # "Invalid or expired token
        except Token.DoesNotExist:
            request.session['errors'] = 'Invalid or expired token'
            return redirect(reverse_lazy('login'))  # "Invalid or expired token

        context = self.get_context_data(**kwargs)
        context['token'] = token

        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['token'] = self.kwargs.get('token')
        return context

    def post(self, request, *args, **kwargs):
        token = kwargs.get('token')
        if not token:
            request.session['errors'] = 'Invalid or expired token'
            return redirect(reverse_lazy('login'))

        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def form_valid(self, form):
        # Process the form
        form.save()
        self.request.session['errors'] = None
        self.request.session['msg'] = "Registration successful!"
        return super().form_valid(form)

    def form_invalid(self, form):
        self.request.session['errors'] = form.errors
        self.request.session['msg'] = "Update failed!"
        return self.render_to_response(self.get_context_data(form=form))


class ForgotPass(FormView):
    template_name = 'login_register/forgot-password.html'
    form_class = ForgotPassForm
    success_url = reverse_lazy('login')

    def form_valid(self, form):
        user_email = form.cleaned_data['email']
        if not user_email:
            messages.error(self.request, "Please enter your email.")
            return redirect("forgot-password")

        try:
            user = User.objects.get(email=user_email)
            token_obj = Token.generate_token(
                token_type=TokenType.PASSWORD_RESET,
                user=user,
                hours_valid=1
            )

            reset_link = self.request.build_absolute_uri(
                reverse('recover-password', kwargs={'token': token_obj.token})
            )

            dojo_logo_url = self.request.build_absolute_uri(static('img/icon.png'))

            html_content = render_to_string(
                'emails/password_reset_email.html',
                {
                    'dojo_logo_url': dojo_logo_url,
                    'reset_link': reset_link,
                    'current_year': datetime.now().year,
                }
            )

            email = EmailMultiAlternatives(
                subject="Password Reset Request",
                body="Use the following link to reset your password: " + reset_link,  # Versión de texto plano
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[user_email],
            )
            email.attach_alternative(html_content, "text/html")
            logo_path = Path(settings.BASE_DIR) / "static" / "img" / "icon.png"
            with logo_path.open('rb') as f:
                msg_image = f.read()
            from email.mime.image import MIMEImage
            image = MIMEImage(msg_image)
            image.add_header('Content-ID', '<dojo_logo>')
            image.add_header('Content-Disposition', 'inline', filename="dojo-logo.png")
            email.attach(image)
            email.send()

            messages.success(self.request, "We have sent a password reset link to your email.")
            return redirect('login')
        except User.DoesNotExist:
            messages.error(self.request, "No user found with that email address.")
            return redirect('forgot-password')
        # return super().form_valid(form)


# Vista de Recuperación de Contraseña
class RecoverPass(TemplateView):
    template_name = 'login_register/recover-password.html'
    form_class = RecoverPassForm
    success_url = reverse_lazy('login')

    def dispatch(self, request, *args, **kwargs):
        self.uidb64 = kwargs.get('uidb64')
        self.token = kwargs.get('token')
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        try:
            uid = force_str(urlsafe_base64_decode(self.uidb64))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None

        token_generator = PasswordResetTokenGenerator()
        if user is not None and token_generator.check_token(user, self.token):
            user.set_password(form.cleaned_data['password1'])
            user.save()
            messages.success(self.request, "Your password has been reset successfully.")
            return super().form_valid(form)
        else:
            messages.error(self.request, "The reset link is invalid or expired.")
            return redirect('forgot-password')

    def form_invalid(self, form):
        self.request.session['errors'] = form.errors
        self.request.session['msg'] = "Update failed!"
        return self.render_to_response(self.get_context_data(form=form))
