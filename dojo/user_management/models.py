import datetime

from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from config.config_vars import ranges


class IDType(models.TextChoices):
    CEDULA_CIUDADANIA = 'CC', 'Cédula de ciudadanía'
    TARJETA_IDENTIDAD = 'TI', 'Tarjeta de Identidad'
    CEDULA_EXTRANJERIA = 'CE', 'Cédula de extranjería'
    PASAPORTE = 'PA', 'Pasaporte'
    OTRO = 'OT', 'Otro'


class Category(models.TextChoices):
    SENSEI = 'S', 'Sensei'
    ESTUDIANTE = 'E', 'Estudiante'


class MedicalConditions(models.TextChoices):
    ENFERMEDADES_CARDIACAS = 'EC', 'Enfermedades Cardiacas'
    HIPERTENSION_ARTERIAL = 'HA', 'Hipertensión Arterial'
    DIABETES = 'D', 'Diabetes'
    ASMA_O_PROBLEMAS_RESPIRATORIOS = 'AoPR', 'Asma O Problemas Respiratorios'
    EPILEPSIA_O_CONVULSIONES = 'EoC', 'Epilepsia O Convulsiones'
    PROBLEMAS_MUSCULOESQUELETICOS = 'PME', 'Problemas Musculoesqueléticos (Ej. Esguinces, Fracturas)'
    OTROS = 'OT', 'Otros'
    NA = 'NA', 'No Aplica'


class PhysicalConditions(models.TextChoices):
    EXCELENTE = 'E', 'Excelente'
    BUENO = 'B', 'Bueno'
    ACEPTABLE = 'A', 'Aceptable'
    NECESITA_MEJORAR = 'I', 'Necesita mejorar'


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
        max_length=2,
        choices=IDType.choices,
        default=IDType.CEDULA_CIUDADANIA
    )
    category = models.CharField(
        max_length=1,
        choices=Category.choices,
        default=Category.ESTUDIANTE
    )
    id_number = models.CharField(max_length=30, unique=True, null=False, blank=False)
    birth_date = models.DateField(default=datetime.datetime(2000, 1, 1))
    birth_place = models.CharField(max_length=30, default='')
    profession = models.CharField(max_length=30, default='')
    eps = models.CharField(max_length=50, default='')
    phone_number = models.CharField(max_length=15, default='')
    address = models.CharField(max_length=255, default='')
    city = models.CharField(max_length=30, default='')
    country = models.CharField(max_length=30, default='')
    email = models.EmailField(max_length=255, null=False, blank=False)
    level = models.CharField(choices=ranges, default=ranges[0])
    parent = models.CharField(max_length=60, null=True, blank=True, default='')
    parent_phone_number = models.CharField(max_length=15, null=True, blank=True, default='')
    accept_inf_cons = models.BooleanField(default=False)
    medical_cond = models.CharField(choices=MedicalConditions.choices, default=MedicalConditions.NA)
    drug_cons = models.CharField(max_length=60, null=True, blank=True, default='')
    allergies = models.CharField(max_length=60, null=True, blank=True, default='')
    other_activities = models.CharField(max_length=60, null=True, blank=True, default='')
    cardio_prob = models.BooleanField(default=False)
    injuries = models.BooleanField(default=False)
    physical_limit = models.BooleanField(default=False)
    # Lost consciousness or lost balance after feeling dizzy
    lost_cons = models.BooleanField('lost consciousness', default=False)
    physical_cond = models.CharField(choices=PhysicalConditions.choices, default=PhysicalConditions.ACEPTABLE)
    # Follow the instructor's recommendations and safety rules during the classes.
    sec_recom = models.BooleanField(default=False)
    # I have read, understand the questions, completed and answered the questionnaire with my acceptance?
    agreement = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)
    date_deactivated = models.DateTimeField(null=True)
    date_reactivated = models.DateTimeField(null=True)
    payment = models.IntegerField(default=0)
    payment_status = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    USERNAME_FIELD = 'id_number'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    objects = UserManager()

    def __str__(self):
        return f'{self.first_name} {self.last_name}'
