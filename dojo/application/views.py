from django.shortcuts import render
from django.http import HttpResponse
from django.views.generic import TemplateView


class Index(TemplateView):
    template_name = 'index.html'

    def get_context_data(self, **kwargs):
        ctx = super(Index, self).get_context_data(**kwargs)
        return ctx

    def get(self, request, *args, **kwargs):
        return render(request, 'pages/attendance.html')
