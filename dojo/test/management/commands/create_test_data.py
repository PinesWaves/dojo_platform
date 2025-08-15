from datetime import datetime, timedelta
from django.core.management.base import BaseCommand
from django.db import connection
from faker import Faker
import logging

from user_management.models import User, Category
from config.config_vars import Ranges
from dashboard.models import Dojo, Training, Technique, TrainingStatus
from django.utils import timezone


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Create and load test data into the database'
    
    # def add_arguments(self, parser):
    #     parser.add_argument(
    #         '--testing',
    #         action='store_true',
    #         help='Reset the database before loading the dataset'
    #     )

    def handle(self, *args, **kwargs):
        # if kwargs['testing']:
        self.fake = Faker()
        self.load_testing_data()

    def load_testing_data(self):
        logger.info('Reset DB from testing data')
        self.stdout.write('Reset DB from testing data')
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

        logger.info('Loading testing data')
        self.load_users()
        self.load_techniques()
        self.load_dojos()
        self.load_trainings()
        logger.info(self.style.SUCCESS('Testing dataset loaded successfully'))
        self.stdout.write(self.style.SUCCESS('Testing dataset loaded successfully'))

    def load_users(self):
        # Create 90 students with random data
        logger.info('Loading users')
        self.stdout.write('Loading users')
        users = []
        for i in range(90):
            gender = self.fake.random_element(elements=('M', 'F'))
            users.append({
                'id_number': self.fake.unique.random_number(digits=10),
                'first_name': self.fake.first_name_male() if gender == 'M' else self.fake.first_name_female(),
                'last_name': self.fake.last_name(),
                'id_type': 'CC',
                'category': 'ST',
                'birth_date': self.fake.date_of_birth(minimum_age=18, maximum_age=25),
                'birth_place': self.fake.city(),
                'gender': gender,
                'profession': self.fake.job()[:30],
                'eps': self.fake.company(),
                'phone_number': self.fake.numerify('###-###-####'),
                'address': self.fake.address(),
                'city': self.fake.city()[:30],
                'country': self.fake.country_code(),
                'email': self.fake.email(),
                'level': self.fake.random_element(elements=[x[0] for x in Ranges.choices][:13]),
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
                'is_active': True if i < 80 else False,  # Last 10 users are inactive
                'is_staff': False,  # Only the first student is staff (Sempai)
                'is_superuser': False
            })

        # Create users in the database
        logger.info('Creating users in the database')
        self.stdout.write('Creating users in the database')
        User.objects.bulk_create([User(**row) for row in users])

        # Following users are created for testing purposes
        logger.info('Creating specific users for testing')
        self.stdout.write('Creating specific users for testing')
        # Create a superuser
        User.objects.create_superuser(
            first_name='jesus',
            last_name='rod',
            password='rosales3',
            id_number=1,
            category=Category.SENSEI
        )
        # Create Sempai with specific data
        User.objects.create_user(
            first_name='alberto',
            last_name='henao',
            id_number=2,
            id_type='CC',
            email='jarh1992@outlook.com',
            category=Category.SEMPAI,
            birth_date=datetime(2000, 1, 1),
            birth_place='Bogotá',
            password = 'rosales3'
        )
        # Create sensei (Dojo 1) with specific data
        User.objects.create_user(
            first_name='cesar',
            last_name='peña',
            id_number=3,
            id_type='CC',
            category=Category.SENSEI,
            birth_date=datetime(1980, 1, 1),
            birth_place='Bogotá',
            password = 'rosales3'
        )
        # Create sensei (Dojo 2) with specific data
        User.objects.create_user(
            first_name=self.fake.first_name(),
            last_name=self.fake.last_name(),
            id_number=4,
            id_type='CC',
            category=Category.SENSEI,
            birth_date=datetime(1980, 1, 1),
            birth_place='Bogotá',
            password = 'rosales3'
        )
        # Create sensei (Dojo 3) with specific data
        User.objects.create_user(
            first_name=self.fake.first_name(),
            last_name=self.fake.last_name(),
            id_number=5,
            id_type='CC',
            category=Category.SENSEI,
            birth_date=datetime(1980, 1, 1),
            birth_place='Bogotá',
            password = 'rosales3'
        )

    def load_techniques(self):
        # Create Techniques
        logger.info('Loading techniques')
        self.stdout.write('Loading techniques')
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
        logger.info('Loading dojos')
        self.stdout.write('Loading dojos')
        dojos = []
        for i in range(3):
            dojos.append({
                'sensei': User.objects.get(id_number=i+3),  # Will be assigned later
                'name': self.fake.company(),
                'address': self.fake.address(),
                'city': self.fake.city(),
                'country': self.fake.country(),
                'phone_number': self.fake.numerify('###-###-####'),
                'email': self.fake.email()
            })

        Dojo.objects.bulk_create([Dojo(**row) for row in dojos])

    def load_trainings(self):
        logger.info('Loading trainings')
        self.stdout.write('Loading trainings')
        # Create 10 Training sessions with different statuses
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
