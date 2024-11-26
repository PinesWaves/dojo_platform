from django.core.management.base import BaseCommand
from datetime import datetime
from user_management.models import Token


class Command(BaseCommand):
    help = "Clean all the expired tokens"

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        Token.objects.filter(expires_at__lte=datetime.now()).delete()
