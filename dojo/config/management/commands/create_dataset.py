import csv
from datetime import datetime
from django.core.management.base import BaseCommand
from user_management.models import User, Category
from dashboard.models import Dojo, Training, Technique


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
        with open('test/data/trainings.csv', newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                tr = Training(**row)
                tr.save()
                tr.techniques.set(Technique.objects.all())
                tr.attendants.set(User.objects.all()[:10])
