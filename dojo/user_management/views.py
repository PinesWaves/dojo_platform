import logging
from datetime import datetime

import math
from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views import View
from django.views.generic import CreateView, UpdateView, DeleteView, TemplateView, FormView
from django.shortcuts import get_object_or_404, render
from django.contrib.auth import get_user_model
from .forms import UserRegisterForm, UserUpdateForm
from .models import Category, Token

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
        error = request.session.pop('error', None)
        msg = request.session.pop('msg', None)
        if user.is_authenticated:  # Redirige si ya está autenticado
            if user.is_superuser or user.category == Category.SENSEI:
                return redirect(reverse_lazy('sensei_dashboard'))  # Redirigir al dashboard del sensei
            elif user.category == Category.ESTUDIANTE:
                return redirect(reverse_lazy('student_dashboard'))  # Redirigir al dashboard del estudiante
        return render(request, self.template_name, {'error': error, 'msg': msg})

    def post(self, request):
        id_number = request.POST.get('id_number')
        password = request.POST.get('password')

        user = authenticate(request, id_number=id_number, password=password)

        if user:
            login(request, user)
            if user.is_superuser or user.category == Category.SENSEI:
                return redirect(reverse_lazy('sensei_dashboard'))  # Redirigir al dashboard del sensei
            elif user.category == Category.ESTUDIANTE:
                return redirect(reverse_lazy('student_dashboard'))  # Redirigir al dashboard del estudiante
            else:
                return redirect(reverse_lazy('login'))  # Página por defecto

        return render(request, self.template_name, {
            'error': 'Invalid credentials',
        })


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
            registration_token = Token.objects.get(token=token)
            if not registration_token.is_valid():
                request.session['error'] = 'Invalid or expired token'
                return redirect(reverse_lazy('login'))  # "Invalid or expired token
        except Token.DoesNotExist:
            request.session['error'] = 'Invalid or expired token'
            return redirect(reverse_lazy('login'))  # "Invalid or expired token

        return super().get(request, *args, **kwargs)

    def form_valid(self, form, request):
        # Process the form
        form.save()
        self.request.session['error'] = None
        self.request.session['msg'] = "Registration successful!"
        return super().form_valid(form)

    def form_invalid(self, form):
        print(form.errors)
        self.object = None
        return self.render_to_response(self.get_context_data(form=form))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        form_instance = kwargs['form'] if 'form' in kwargs else self.get_form_class()()  # Create a blank form instance
        form_fields = list(form_instance)  # Convert form fields to a list

        total_sections = math.ceil(len(form_fields) / 6)  # Calculate the number of sections
        sectioned_fields = [
            (i + 1, form_fields[i * 6: (i + 1) * 6])  # (section_number, [fields])
            for i in range(total_sections)
        ]  # Creates a list of tuples (1, [fields]), (2, [fields]) ...

        context.update({
            'sectioned_fields': sectioned_fields,  # List of (section_number, fields)
            'total_sections': total_sections,  # Number of sections
            'token': self.kwargs.get('token'),  # Token passed in the URL
            # 'error': form.errors.get('__all__'),  # Form errors
        })
        return context

    def post(self, request, *args, **kwargs):
        token = kwargs.get('token')
        if not token:
            request.session['error'] = 'Invalid or expired token'
            return redirect(reverse_lazy('login'))

        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form, request)
        else:
            return self.form_invalid(form)



# Vista de Actualización de Usuario
class UpdateUserView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = UserUpdateForm
    template_name = 'user_management/update_user.html'
    success_url = reverse_lazy('attendance')

    def get_object(self, queryset=None):
        # Sensei puede editar cualquier usuario, otros solo su propio perfil
        user = get_object_or_404(User, pk=self.kwargs['pk'])
        if self.request.user.categoria == Category.SENSEI or self.request.user == user:
            return user
        return self.request.user

# Vista de Desactivación de Usuario (solo Sensei)
class DeleteUserView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = User
    template_name = 'user_management/delete_user.html'
    success_url = reverse_lazy('login')

    def test_func(self):
        return self.request.user.categoria == Category.SENSEI

    def form_valid(self, form):
        user = self.get_object()
        user.is_active = False  # Desactivar usuario en vez de eliminar
        user.save()
        return super().form_valid(form)


class RecoverPass(TemplateView):
    model = User
    fields = ['password']
    template_name = 'login_register/recover-password.html'
    success_url = reverse_lazy('login')


class ForgotPass(TemplateView):
    model = User
    fields = ['email']
    template_name = 'login_register/forgot-password.html'
    success_url = reverse_lazy('/')


def deactivate_user(email, **extra_fields):
    # email = self.normalize_email(email)
    user = User(email=email, **extra_fields)
    user.is_active = False
    user.date_deactivated = datetime.now()
    user.save()
