from io import BytesIO
import qrcode
from django.core.exceptions import ValidationError
from django.core.files import File
from django.db import models
from secrets import token_urlsafe

from user_management.models import User, Category


class TechniqueCategory(models.TextChoices):
    ARTICULAR = 'CA', 'Calentamiento Articular'
    ESTIRAMIENTO = 'ES', 'Estiramiento'
    KIHON = 'KI', 'Kihon'
    KUMITE = 'KU', 'Kumite'
    PRINCIPIANTE = 'PR', 'Principiante'
    INTERMEDIO = 'I', 'Intermedio'
    AVANZADO = 'AV', 'Avanzado'


class Technique(models.Model):
    name = models.CharField(max_length=100)
    image = models.ImageField(upload_to='techniques/', blank=True, null=True, default='techniques/default_technique.jpg')
    category = models.CharField(choices=TechniqueCategory.choices, default=TechniqueCategory.KIHON)


class Training(models.Model):
    date = models.DateTimeField(auto_now=True)
    status = models.BooleanField(default=True)  # True: Active (not finished); False: finished
    training_code = models.CharField(max_length=100, blank=True)
    qr_image = models.ImageField(upload_to='qr_codes/', blank=True, null=True)
    attendants = models.ManyToManyField(User, related_name="trainings", blank=True)
    techniques = models.ManyToManyField(Technique, related_name="techniques")

    def save(self, *args, **kwargs):

        if self.status:
            self.training_code = token_urlsafe(30)
            # Generar el QR a partir del código
            qr = qrcode.QRCode(version=1, box_size=10, border=5)
            qr.add_data(self.training_code)
            qr.make(fit=True)

            # Guardar la imagen en un campo ImageField
            qr_image = qr.make_image(fill_color="black", back_color="white")
            buffer = BytesIO()
            qr_image.save(buffer, format="PNG")
            buffer.seek(0)
            self.qr_image.save(f"{self.training_code}.png", File(buffer), save=False)
        super().save(*args, **kwargs)


class Dojo(models.Model):
    name = models.CharField(max_length=100)
    image = models.ImageField(upload_to='qr_codes/', blank=True, null=True)
    description = models.TextField()
    sensei: User = models.OneToOneField(User, related_name="sensei", on_delete=models.DO_NOTHING)
    students = models.ManyToManyField(User, related_name="students")

    def clean(self):
        """
        Ensure that the 'sensei' is a user with category SENSEI.
        """
        if self.sensei and self.sensei.category != Category.SENSEI:
            raise ValidationError("The selected user must have the category 'SENSEI'.")

    def save(self, *args, **kwargs):
        """
        Call clean() to enforce validation before saving.
        """
        self.clean()
        super().save(*args, **kwargs)
