import uuid
from datetime import datetime, timedelta
from django.utils import timezone
from django.utils.timezone import now

from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin

from utils.config_vars import Ranges


class IDType(models.TextChoices):
    CITIZENSHIP_CARD = 'CC', 'Citizenship card'
    IDENTITY_CARD = 'IC', 'Identity Card'
    ALIEN_CARD = 'AR', 'Alien Registration Card'
    PASSPORT = 'PA', 'Passport'
    OTHER = 'OT', 'Other'


class Category(models.TextChoices):
    SENSEI = 'SE', 'Sensei'
    SEMPAI = 'SP', 'Sempai'
    STUDENT = 'ST', 'Student'


class MedicalConditions(models.TextChoices):
    CARDIAC_DISEASES = 'CD', 'Cardiac Diseases'
    ARTERIAL_HYPERTENSION = 'AH', 'Arterial Hypertension'
    DIABETES = 'D', 'Diabetes'
    ASTHMA_OR_RESPIRATORY_PROBLEMS = 'AR', 'Asthma or respiratory problems'
    EPILEPSY_OR_SEIZURES = 'ES', 'Epilepsy or Seizures'
    MUSCULOSKELETAL_PROBLEMS = 'MP', 'Musculoskeletal Problems (e.g. Sprains, Fractures)'
    OTHERS = 'OT', 'Others'
    NA = 'NA', 'No aplicable'


class PhysicalConditions(models.TextChoices):
    EXCELLENT = 'E', 'Excellent'
    GOOD = 'G', 'Good'
    ACCEPTABLE = 'A', 'Acceptable'
    NEEDS_IMPROVEMENT = 'I', 'Needs improvement'


class Genders(models.TextChoices):
    MALE = 'M', 'Male'
    FEMALE = 'F', 'Female'


class UserManager(BaseUserManager):
    def create_user(self, id_number, password=None, **extra_fields):
        """
        Crea y guarda un usuario con el número de ID y la contraseña proporcionados.
        """
        if not id_number:
            raise ValueError('The ID number field must be set')

        user = self.model(id_number=id_number, **extra_fields)
        user.set_password(password)  # Establece la contraseña de manera segura
        user.save(using=self._db)  # Guarda el usuario en la base de datos
        return user

    def create_superuser(self, id_number, password=None, **extra_fields):
        """
        Crea y guarda un superusuario con el número de ID y la contraseña proporcionados.
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        # Verificar que las propiedades esenciales para el superusuario estén establecidas
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True')

        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True')

        # Crear un superusuario usando el método `create_user`
        return self.create_user(id_number, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    first_name = models.CharField(max_length=30, null=False, blank=False)
    last_name = models.CharField(max_length=30, null=False, blank=False)
    id_type = models.CharField(
        choices=IDType.choices,
        default=IDType.CITIZENSHIP_CARD
    )
    category = models.CharField(
        choices=Category.choices,
        default=Category.STUDENT
    )
    id_number = models.CharField(max_length=30, unique=True, null=False, blank=False)
    birth_date = models.DateField(default=datetime(2000, 1, 1), null=False, blank=False)
    birth_place = models.CharField(max_length=30, default='')
    gender = models.CharField(choices=Genders.choices, default=Genders.MALE)
    profession = models.CharField(max_length=30, default='')
    eps = models.CharField(max_length=50, default='')
    phone_number = models.CharField(max_length=15, null=False, blank=False)
    address = models.CharField(max_length=255, default='')
    city = models.CharField(max_length=30, default='')
    country = models.CharField(max_length=30, default='')
    email = models.EmailField(max_length=255, null=False, blank=False)
    picture = models.ImageField(upload_to='profile_imgs/', blank=True, null=True)
    level = models.CharField(choices=Ranges.choices, default=Ranges.K10)
    parent = models.CharField(max_length=60, null=True, blank=True, default='')
    parent_phone_number = models.CharField(max_length=15, null=True, blank=True, default='')
    medical_cond = models.CharField(choices=MedicalConditions.choices, default=MedicalConditions.NA)
    drug_cons = models.CharField(max_length=60, null=True, blank=True, default='')
    allergies = models.CharField(max_length=60, null=True, blank=True, default='')
    other_activities = models.CharField(max_length=60, null=True, blank=True, default='')
    cardio_prob = models.BooleanField(default=False)
    injuries = models.BooleanField(default=False)
    physical_limit = models.BooleanField(default=False)
    # Lost consciousness or lost balance after feeling dizzy
    lost_cons = models.BooleanField('lost consciousness', default=False)
    physical_cond = models.CharField(choices=PhysicalConditions.choices, default=PhysicalConditions.ACCEPTABLE)
    # Follow the instructor's recommendations and safety rules during the classes.
    sec_recom = models.BooleanField(default=False)
    # I have read, understand the questions, completed and answered the questionnaire with my acceptance?
    agreement = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now, editable=True)
    date_deactivated = models.DateTimeField(null=True)
    date_reactivated = models.DateTimeField(null=True)
    payment = models.IntegerField(default=0)
    payment_status = models.BooleanField(default=True)
    accept_regulations = models.BooleanField(default=False)
    accept_inf_cons = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    USERNAME_FIELD = 'id_number'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    objects = UserManager()

    def __str__(self):
        return f'{self.first_name} {self.last_name}'


class TokenType(models.TextChoices):
    SIGNUP = 'SU', 'Sign up'
    PASSWORD_RESET  = 'PR', 'Password reset'
    OTHER = 'O', 'Other'


class Token(models.Model):
    user = models.ForeignKey('User', null=True, blank=True, on_delete=models.CASCADE)
    token = models.CharField(max_length=100, unique=True)  # The generated token
    created_at = models.DateTimeField(auto_now_add=True)  # Timestamp for token creation
    expires_at = models.DateTimeField()  # Expiration timestamp
    type = models.CharField(
        max_length=2,
        choices=TokenType.choices,
        default=TokenType.OTHER
    )  # Task associated with the token

    @classmethod
    def generate_token(cls, token_type=TokenType.OTHER, user=None, hours_valid=1):
        """
        Genera un token único con una fecha de expiración.
        """
        token_str = uuid.uuid4().hex
        return cls.objects.create(
            token=token_str,
            user=user,
            type=token_type,
            expires_at=now() + timedelta(hours=hours_valid)
        )

    def is_valid(self):
        """Check if the token is still valid."""
        return now() <= self.expires_at

    def __str__(self):
        return f"{self.type} - {self.token}"
