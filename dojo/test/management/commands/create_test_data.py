import calendar
import random
from datetime import datetime, timedelta
from decouple import config

from django.apps import apps
from django.contrib.auth.hashers import make_password
from django.core.management.base import BaseCommand
from django.db import connection, transaction
from faker import Faker

from user_management.models import User, Category
from utils.config_vars import Ranges
from dashboard.models import Dojo, Training, Technique, TrainingStatus, TrainingType, Attendance, TrainingScheduling
from django.utils import timezone


class Command(BaseCommand):
    help = 'Create and load test data into the database'
    
    # def add_arguments(self, parser):
    #     parser.add_argument(
    #         '--testing',
    #         action='store_true',
    #         help='Reset the database before loading the dataset'
    #     )

    def handle(self, *args, **kwargs):
        if config('DOJO_ENV').lower() in ['production', 'prod']:
            self.stdout.write(self.style.ERROR('❌  Cannot load testing data in production environment.'))
            return
        self.fake = Faker()
        self.load_testing_data()

    def load_testing_data(self):
        self.stdout.write('Reset DB from testing data')
        self.truncate_all_tables_and_reset_sequences()
        self.load_users()
        self.load_techniques()
        self.load_dojos()
        self.load_schedules()
        self.load_trainings()
        self.load_attendances()
        self.stdout.write(self.style.SUCCESS(f'✅  Testing dataset loaded successfully'))

    def load_users(self):
        # Create 90 students with random data
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
                'date_joined': timezone.now(),
                'payment': self.fake.random_int(min=0, max=1000),
                'payment_status': self.fake.boolean(),
                'is_active': True if i < 80 else False,  # Last 10 users are inactive
                'is_staff': False,  # Only the first student is staff (Sempai)
                'is_superuser': False,
                'password': make_password('rosales3')
            })

        # Create users in the database
        self.stdout.write('Creating users in the database')
        User.objects.bulk_create([User(**row) for row in users])

        # Following users are created for testing purposes
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

        self.stdout.write(self.style.SUCCESS(f"✅  Users loaded successfully."))

    def load_techniques(self):
        # Create Techniques
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
                'type': 'KI'
            })
        
        for row in techniques:
            Technique.objects.create(**row)

        self.stdout.write(self.style.SUCCESS(f"✅  Techniques loaded successfully."))

    def load_dojos(self):
        # Create 3 Dojos
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
        self.stdout.write(self.style.SUCCESS(f"✅  Dojos loaded successfully."))


    def load_schedules(self):
        """
        Creates TrainingScheduling entries from TEST_SCHEDULES, mirroring the
        recurring schedule used by get_test_training_dates.
        """
        self.stdout.write("Loading training schedules...")
        from datetime import time as dt_time
        schedules = []
        for day_of_week, slots in TEST_SCHEDULES.items():
            for hour, minute in slots:
                schedules.append(TrainingScheduling(
                    day_of_week=day_of_week,
                    time=dt_time(hour, minute),
                ))
        TrainingScheduling.objects.bulk_create(schedules)
        self.stdout.write(self.style.SUCCESS(f"✅  Training schedules loaded successfully."))

    def load_trainings(self):
        """
        Create test trainings with different statuses based on the date:
          - Futures → SCHEDULED
          - Currently in progress → ONGOING
          - Past → FINISHED
          - A percentage of past/future → CANCELED
        """

        self.stdout.write("Loading trainings...")
        dates = get_test_training_dates()
        now = timezone.now()
        for d in dates:
            end_time = d + timedelta(minutes=90)
            if d > now:
                status = TrainingStatus.SCHEDULED
            elif d <= now <= end_time:
                status = TrainingStatus.ONGOING
            else:
                status = random.choices(
                    [TrainingStatus.FINISHED, TrainingStatus.CANCELED, TrainingStatus.ONGOING],
                    weights=[20,5,1],
                    k=1
                )[0]

            Training.objects.create(
                date=d,
                type=random.choice(TrainingType.values),
                status=status,
                details=f"Training {calendar.day_name[d.weekday()]} {d.hour:02d}:{d.minute:02d}",
                location="Main Dojo",
            )
        self.stdout.write(self.style.SUCCESS(f"✅  Trainings loaded successfully."))


    def load_attendances(self):
        """
        Creates test assistances:
          - Only for training sessions that are not cancelled.
          - Marks some students as present, and others absent.
        """

        self.stdout.write("Loading attendances...")

        # Filtrar entrenamientos válidos
        trainings = Training.objects.exclude(status__in=[TrainingStatus.CANCELED, TrainingStatus.SCHEDULED])

        # Tomar todos los estudiantes registrados
        students = User.objects.filter(category=Category.STUDENT, is_active=True)

        if not students.exists():
            self.stdout.write(self.style.WARNING("No students to register attendance."))
            return

        for training in trainings:
            # Seleccionar aleatoriamente quién asistió
            attending_students = random.sample(
                list(students), k=random.randint(5, 30)
            )

            for student in students:
                Attendance.objects.create(
                    training=training,
                    student=student,
                    status='P' if student in attending_students else 'A',
                    timestamp=training.date + timedelta(minutes=random.randint(0, 15)),  # Arrival time
                    notes=''  # Optional notes
                )
        self.stdout.write(self.style.SUCCESS(f"✅  Assists loaded successfully."))


    def truncate_all_tables_and_reset_sequences(self):
        """
        Deletes all records from all tables and resets the ID sequence counters to 1 in PostgreSQL.
        """
        with connection.cursor() as cursor:
            # Disables FK restrictions temporarily
            cursor.execute("SET session_replication_role = 'replica';")

            for model in apps.get_models():
                table = model._meta.db_table

                # Deletes all data in the table
                cursor.execute(f'TRUNCATE TABLE "{table}" RESTART IDENTITY CASCADE;')

            # Restore FK restrictions
            cursor.execute("SET session_replication_role = 'origin';")

        # Confirm transaction
        transaction.commit()
        self.stdout.write(self.style.SUCCESS(f"✅  All tables have been truncated and sequences reset."))


TEST_SCHEDULES = {
    0: [(17, 0), (19, 0)],  # lunes
    1: [(19, 0)],            # martes
    2: [(17, 0), (19, 0)],  # miércoles
    3: [(19, 0)],            # jueves
    4: [(17, 0), (19, 0)],  # viernes
    5: [(8, 0), (10, 0)],   # sábado
}


def get_test_training_dates():
    """
    Returns a list of datetime objects representing test training dates and times 2 weeks before and after today's date.
    """
    schedules = TEST_SCHEDULES

    today = timezone.now()
    days_before = 14
    days_after = 14
    dates = []
    for i in range(-days_before, days_after + 1):
        day = today + timedelta(days=i)
        if day.weekday() in [0, 1, 2, 3, 4, 5]:  # Monday-Saturday
            aware_day = timezone.make_aware(
                datetime(
                    day.year,
                    day.month,
                    day.day,
                    schedules[day.weekday()][0][0],
                    0,
                )
            )
            dates.append(aware_day)
            if day.weekday() in [0, 2, 4, 5]:  # Monday-Friday + Saturday
                aware_day = timezone.make_aware(
                    datetime(
                        day.year,
                        day.month,
                        day.day,
                        schedules[day.weekday()][1][0],
                        0,
                    )
                )
                dates.append(aware_day)
    dates.reverse()  # Optional: earliest to latest
    return dates
