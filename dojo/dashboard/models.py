import hashlib
from datetime import datetime
from io import BytesIO
import qrcode
from django.core.files import File
from django.db import models
import bcrypt


class Technique(models.Model):
    name = models.CharField(max_length=100)
    image = models.ImageField(upload_to='qr_codes/', blank=True, null=True)  # Imagen QR


class Training(models.Model):
    date = models.DateField(auto_now=True)
    start_time = models.TimeField(default=datetime.now())
    training_code = models.CharField(max_length=100, unique=True, blank=True)
    qr_image = models.ImageField(upload_to='qr_codes/', blank=True, null=True)  # Imagen QR
    techniques = models.ManyToManyField(Technique)

    # Sal y pepper para el código
    SALT = ""

    def save(self, *args, **kwargs):
        if not self.training_code:  # Solo generar si no existe un código
            # Generar el código basado en fecha y salt
            self.SALT = bcrypt.gensalt()
            hashed = bcrypt.hashpw(datetime.now().strftime('%Y%m%d%H%M%S'), self.SALT)
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
