from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views import View
from django.http import HttpResponseForbidden

from user_management.models import Category

class UserCategoryRequiredMixin(View):
    allowed_categories = [Category.SENSEI]

    def dispatch(self, request, *args, **kwargs):
        user = request.user
        if user.is_authenticated:
            if user.category in self.allowed_categories or user.is_superuser:
                return super().dispatch(request, *args, **kwargs)
            return redirect(reverse_lazy('student_dashboard'))
        return redirect(reverse_lazy('login'))
