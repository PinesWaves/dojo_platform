from datetime import datetime

from django.shortcuts import render
from django.views.generic import TemplateView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import User


class Register(CreateView):
    model = User
    template_name = 'login_register/register.html'
    success_url = reverse_lazy('login')


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


class CreateUser(LoginRequiredMixin, CreateView):
    model = User
    fields = ['email', 'first_name', 'last_name', 'password']
    template_name = 'create_user.html'
    success_url = reverse_lazy('user_list')


class UpdateUser(LoginRequiredMixin, UpdateView):
    model = User
    fields = ['email', 'first_name', 'last_name', 'password']
    template_name = 'update_user.html'
    success_url = reverse_lazy('user_list')


def deactivate_user(email, **extra_fields):
    # email = self.normalize_email(email)
    user = User(email=email, **extra_fields)
    user.is_active = False
    user.date_deactivated = datetime.now()
    user.save()


class DeleteUser(LoginRequiredMixin, DeleteView):
    model = User
    template_name = 'delete_user.html'
    success_url = reverse_lazy('user_list')


def user_list(request):
    users = User.objects.all()
    return render(request, 'user_list.html', {'users': users})
