# Generated by Django 5.0.9 on 2024-11-17 20:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user_management', '0007_user_city_user_country'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='id_number',
            field=models.CharField(max_length=30, unique=True),
        ),
    ]
