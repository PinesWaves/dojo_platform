# Generated by Django 5.0.6 on 2024-07-05 14:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user_management', '0002_user_address_user_date_reactivated_user_phone_number_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='payment',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='user',
            name='payment_status',
            field=models.BooleanField(default=True),
        ),
    ]