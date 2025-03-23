import csv
from datetime import datetime, timedelta
from django.core.management.base import BaseCommand
from user_management.models import User, Category
from dashboard.models import Dojo, Training, Technique
from django.utils import timezone


class Command(BaseCommand):
    help = 'Load dataset from CSV files into the database'

    def handle(self, *args, **kwargs):
        Training.objects.all().delete()
        Dojo.objects.all().delete()
        Technique.objects.all().delete()
        User.objects.all().delete()
        self.load_users()
        self.load_techniques()
        self.load_dojos()
        self.load_trainings()
        self.stdout.write(self.style.SUCCESS('Dataset loaded successfully'))

    def load_users(self):
        with open('test/data/users.csv', newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                User.objects.create_user(**row)

        User.objects.create_superuser(first_name='jesus', last_name='rod', password='rosales3', id_number=1)

    def load_techniques(self):
        with open('test/data/techniques.csv', newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                Technique.objects.create(**row)

    def load_dojos(self):
        with open('test/data/dojos.csv', newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            i = 0
            for row in reader:
                row['sensei'] = User.objects.filter(category=Category.SENSEI)[i]
                Dojo.objects.create(**row)
                i += 1
                if i == 3:
                    i = 0

    def load_trainings(self):
        today = datetime.now().date()
        for i in range(1, 11):
            for j in range(2):
                tr = Training(
                    date=timezone.make_aware(
                        datetime(today.year, today.month, today.day, 17, 0) - timedelta(days=i - 1)
                        if j == 0
                        else datetime(today.year, today.month, today.day, 19, 0) - timedelta(days=i - 1)
                    ),
                    status=True if i == 1 else False,
                    location='Seishin Dojo'
                )
                tr.save()
                tr.attendants.set(User.objects.all()[:10])
                tr.techniques.set(Technique.objects.all())
