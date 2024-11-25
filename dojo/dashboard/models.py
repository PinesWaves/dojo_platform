import hashlib
from datetime import datetime
from io import BytesIO
import qrcode
from django.core.exceptions import ValidationError
from django.core.files import File
from django.db import models
import bcrypt

from user_management.models import User, Category


class Technique(models.Model):
    name = models.CharField(max_length=100)
    image = models.ImageField(upload_to='qr_codes/', blank=True, null=True)


class Training(models.Model):
    date = models.DateField(auto_now=True)
    status = models.BooleanField(default=True)
    training_code = models.CharField(max_length=100, blank=True)
    qr_image = models.ImageField(upload_to='qr_codes/', blank=True, null=True)
    attendants = models.ManyToManyField(User, related_name="trainings")
    techniques = models.ManyToManyField(Technique, related_name="techniques")

    def save(self, *args, **kwargs):
        if not self.training_code:  # Solo generar si no existe un código
            # Generar el código basado en fecha y salt
            salt = bcrypt.gensalt()
            hashed = bcrypt.hashpw(datetime.now().strftime('%Y%m%d%H%M%S'), salt)
            self.training_code = hashlib.sha256(hashed.encode()).hexdigest()[:10]

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
