# Generated by Django 5.0.9 on 2024-11-29 03:54

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0002_remove_training_start_time_training_attendants_and_more'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.RemoveField(
            model_name='training',
            name='qr_image',
        ),
        migrations.RemoveField(
            model_name='training',
            name='training_code',
        ),
        migrations.AddField(
            model_name='technique',
            name='category',
            field=models.CharField(choices=[('CA', 'Calentamiento Articular'), ('ES', 'Estiramiento'), ('KI', 'Kihon'), ('KU', 'Kumite')], default='KI'),
        ),
        migrations.AlterField(
            model_name='technique',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to='techniques/'),
        ),
        migrations.AlterField(
            model_name='training',
            name='attendants',
            field=models.ManyToManyField(blank=True, related_name='trainings', to=settings.AUTH_USER_MODEL),
        ),
    ]
