# Generated by Django 5.0.9 on 2024-11-30 06:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0004_training_qr_image_training_training_code'),
    ]

    operations = [
        migrations.AlterField(
            model_name='technique',
            name='image',
            field=models.ImageField(blank=True, default='techniques/default_technique.jpg', null=True, upload_to='techniques/'),
        ),
    ]
