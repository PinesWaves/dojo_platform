import csv
from faker import Faker
from datetime import datetime, timedelta

fake = Faker()

# Create students
users = []
for _ in range(90):
    users.append({
        'id_number': fake.unique.random_number(digits=10),
        'first_name': fake.first_name(),
        'last_name': fake.last_name(),
        'id_type': 'CC',
        'category': 'ST',
        'birth_date': fake.date_of_birth(minimum_age=18, maximum_age=25),
        'birth_place': fake.city(),
        'gender': fake.random_element(elements=('M', 'F')),
        'profession': fake.job()[:30],
        'eps': fake.company(),
        'phone_number': fake.numerify('###-###-####'),
        'address': fake.address(),
        'city': fake.city()[:30],
        'country': fake.country()[:30],
        'email': fake.email(),
        'level': 'K10',
        # 'parent': fake.name(),
        # 'parent_phone_number': fake.phone_number(),
        'accept_inf_cons': True,
        'medical_cond': 'NA',
        'drug_cons': '',
        'allergies': '',
        'other_activities': '',
        'cardio_prob': fake.boolean(),
        'injuries': fake.boolean(),
        'physical_limit': fake.boolean(),
        'lost_cons': fake.boolean(),
        'physical_cond': 'A',
        'sec_recom': True,
        'agreement': True,
        'date_joined': datetime.now(),
        'payment': fake.random_int(min=0, max=1000),
        'payment_status': fake.boolean(),
        'is_active': True,
        'is_staff': False,
        'is_superuser': False
    })

# Create Senseis
for _ in range(3):
    users.append({
        'id_number': fake.unique.random_number(digits=10),
        'first_name': fake.first_name(),
        'last_name': fake.last_name(),
        'id_type': 'CC',
        'category': 'SE',
        'birth_date': fake.date_of_birth(minimum_age=30, maximum_age=50),
        'birth_place': fake.city(),
        'gender': fake.random_element(elements=('M', 'F')),
        'profession': fake.job()[:30],
        'eps': fake.company(),
        'phone_number': fake.numerify('###-###-####'),
        'address': fake.address(),
        'city': fake.city()[:30],
        'country': fake.country()[:30],
        'email': fake.email(),
        'level': 'K10',
        # 'parent': fake.name(),
        # 'parent_phone_number': fake.phone_number(),
        'accept_inf_cons': True,
        'medical_cond': 'NA',
        'drug_cons': '',
        'allergies': '',
        'other_activities': '',
        'cardio_prob': fake.boolean(),
        'injuries': fake.boolean(),
        'physical_limit': fake.boolean(),
        'lost_cons': fake.boolean(),
        'physical_cond': 'A',
        'sec_recom': True,
        'agreement': True,
        'date_joined': datetime.now(),
        'payment': fake.random_int(min=0, max=1000),
        'payment_status': fake.boolean(),
        'is_active': True,
        'is_staff': True,
        'is_superuser': False
    })

# Create Dojos
dojos = []
for _ in range(3):
    dojos.append({
        'name': fake.company(),
        'address': fake.address(),
        'city': fake.city(),
        'country': fake.country(),
        'phone_number': fake.numerify('###-###-####'),
        'email': fake.email()
    })

# Create Trainings (active)
trainings = []
for _ in range(21):
    trainings.append({
        'date': datetime.now() + timedelta(days=1),
        'status': True
    })

# Create Trainings (finished)
for _ in range(9):
    trainings.append({
        'date': datetime.now() + timedelta(days=2),
        'status': False
    })

# Create Techniques
techniques = [
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
        'name': techniques[i],
        'category': 'K'
    })

# Write to CSV
with open('data/users.csv', 'w', newline='') as csvfile:
    fieldnames = users[0].keys()
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(users)

with open('data/dojos.csv', 'w', newline='') as csvfile:
    fieldnames = dojos[0].keys()
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(dojos)

with open('data/trainings.csv', 'w', newline='') as csvfile:
    fieldnames = trainings[0].keys()
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(trainings)
