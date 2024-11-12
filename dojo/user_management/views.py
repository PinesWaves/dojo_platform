import logging
from datetime import datetime

from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import CreateView, UpdateView, DeleteView, TemplateView
from django.shortcuts import get_object_or_404, render
from django.contrib.auth import get_user_model
from .forms import UserRegisterForm, UserUpdateForm
from .models import Category

User = get_user_model()

# Vista de Registro
class RegisterView(CreateView):
    model = User
    form_class = UserRegisterForm
    template_name = 'login_register/register.html'
    success_url = reverse_lazy('login')

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


def user_list(request):
    users = User.objects.all()
    return render(request, 'user_list.html', {'users': users})
