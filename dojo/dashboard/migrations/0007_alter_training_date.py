# Generated by Django 5.0.9 on 2025-02-12 03:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0006_alter_technique_category'),
    ]

    operations = [
        migrations.AlterField(
            model_name='training',
            name='date',
            field=models.DateTimeField(auto_now=True),
        ),
    ]
