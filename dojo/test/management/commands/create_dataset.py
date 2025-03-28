import csv
from datetime import datetime, timedelta
from django.core.management.base import BaseCommand
from django.db import connection
from faker import Faker

from user_management.models import User, Category
from dashboard.models import Dojo, Training, Technique, TrainingStatus
from django.utils import timezone


class Command(BaseCommand):
    help = 'Load dataset from CSV files into the database'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--testing',
            action='store_true',
            help='Reset the database before loading the dataset'
        )

    def handle(self, *args, **kwargs):
        if kwargs['testing']:
            self.fake = Faker()
            self.load_testing_data()        

    def load_testing_data(self):
        Training.objects.all().delete()
        Dojo.objects.all().delete()
        Technique.objects.all().delete()
        User.objects.all().delete()

        # Reset primary key sequences
        with connection.cursor() as cursor:
            cursor.execute("SELECT setval(pg_get_serial_sequence('dashboard_training', 'id'), 1, false);")
            cursor.execute("SELECT setval(pg_get_serial_sequence('dashboard_dojo', 'id'), 1, false);")
            cursor.execute("SELECT setval(pg_get_serial_sequence('dashboard_technique', 'id'), 1, false);")
            cursor.execute("SELECT setval(pg_get_serial_sequence('user_management_user', 'id'), 1, false);")

        self.load_users()
        self.load_techniques()
        self.load_dojos()
        self.load_trainings()
        self.stdout.write(self.style.SUCCESS('Testing dataset loaded successfully'))
    
    def load_users(self):
        # Create 90 students with random data
        users = []
        for _ in range(90):
            users.append({
                'id_number': self.fake.unique.random_number(digits=10),
                'first_name': self.fake.first_name(),
                'last_name': self.fake.last_name(),
                'id_type': 'CC',
                'category': 'ST',
                'birth_date': self.fake.date_of_birth(minimum_age=18, maximum_age=25),
                'birth_place': self.fake.city(),
                'gender': self.fake.random_element(elements=('M', 'F')),
                'profession': self.fake.job()[:30],
                'eps': self.fake.company(),
                'phone_number': self.fake.numerify('###-###-####'),
                'address': self.fake.address(),
                'city': self.fake.city()[:30],
                'country': self.fake.country()[:30],
                'email': self.fake.email(),
                'level': 'K10',
                'accept_inf_cons': True,
                'medical_cond': 'NA',
                'drug_cons': '',
                'allergies': '',
                'other_activities': '',
                'cardio_prob': self.fake.boolean(),
                'injuries': self.fake.boolean(),
                'physical_limit': self.fake.boolean(),
                'lost_cons': self.fake.boolean(),
                'physical_cond': 'A',
                'sec_recom': True,
                'agreement': True,
                'date_joined': datetime.now(),
                'payment': self.fake.random_int(min=0, max=1000),
                'payment_status': self.fake.boolean(),
                'is_active': True,
                'is_staff': False,
                'is_superuser': False
            })
        # Create 3 senseis with random data
        for _ in range(3):
            users.append({
                'id_number': self.fake.unique.random_number(digits=10),
                'first_name': self.fake.first_name(),
                'last_name': self.fake.last_name(),
                'id_type': 'CC',
                'category': 'SE',
                'birth_date': self.fake.date_of_birth(minimum_age=30, maximum_age=50),
                'birth_place': self.fake.city(),
                'gender': self.fake.random_element(elements=('M', 'F')),
                'profession': self.fake.job()[:30],
                'eps': self.fake.company(),
                'phone_number': self.fake.numerify('###-###-####'),
                'address': self.fake.address(),
                'city': self.fake.city()[:30],
                'country': self.fake.country()[:30],
                'email': self.fake.email(),
                'level': 'K10',
                'accept_inf_cons': True,
                'medical_cond': 'NA',
                'drug_cons': '',
                'allergies': '',
                'other_activities': '',
                'cardio_prob': self.fake.boolean(),
                'injuries': self.fake.boolean(),
                'physical_limit': self.fake.boolean(),
                'lost_cons': self.fake.boolean(),
                'physical_cond': 'A',
                'sec_recom': True,
                'agreement': True,
                'date_joined': datetime.now(),
                'payment': self.fake.random_int(min=0, max=1000),
                'payment_status': self.fake.boolean(),
                'is_active': True,
                'is_staff': True,
                'is_superuser': False
            })

        for row in users:
            User.objects.create_user(**row)

        User.objects.create_superuser(first_name='jesus', last_name='rod', password='rosales3', id_number=1)

    def load_techniques(self):
        # Create Techniques
        techniques = []
        tcs_list = [
            "Nukiite (ataque con la punta de los dedos)",
            "Yoko-kekomi (patada lateral penetrante)",
            "Keri (patada)",
            "Oi-zuki (golpe con desplazamiento)",
            "Haishu-uke (bloqueo con el dorso de la mano)",
            "Jun-zuki (golpe)",
            "Tsuki (golpe de puño)",
            "Uchi (golpe)",
            "Tate-zuki (golpe vertical)",
            "Yoko-keage (patada lateral ascendente)",
            "Uke (bloqueo)",
        ]
        for i in range(11):
            techniques.append({
                'name': tcs_list[i],
                'category': 'K'
            })
        
        for row in techniques:
            Technique.objects.create(**row)

    def load_dojos(self):
        # Create 3 Dojos
        dojos = []
        for _ in range(3):
            dojos.append({
                'name': self.fake.company(),
                'address': self.fake.address(),
                'city': self.fake.city(),
                'country': self.fake.country(),
                'phone_number': self.fake.numerify('###-###-####'),
                'email': self.fake.email()
            })
        
        i = 0
        for row in dojos:
            try:
                row['sensei'] = User.objects.filter(category=Category.SENSEI)[i]
            except:
                breakpoint()
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
                    status=TrainingStatus.AGENDADO if i == 1 else TrainingStatus.CANCELADO if i == 2 else TrainingStatus.FINALIZADO,
                    location='Seishin Dojo'
                )
                tr.save()
                tr.attendants.set(User.objects.all()[:10])
                tr.techniques.set(Technique.objects.all())
