# middlewares.py
from django.contrib import messages

class ClearMessagesIfLoggedOutMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Si el usuario no está autenticado, limpia los mensajes
        if not request.user.is_authenticated:
            list(messages.get_messages(request))  # Limpia mensajes

        return self.get_response(request)
