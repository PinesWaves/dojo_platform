# Generated by Django 5.0.11 on 2025-03-05 00:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user_management', '0015_alter_user_category_alter_user_id_type_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='level',
            field=models.CharField(choices=[('10k', 'Beginner'), ('9k', '9th kyu'), ('8k', '8th kyu'), ('7k', '7th kyu'), ('6k', '6th kyu'), ('5k', '5th kyu'), ('4k', '4th kyu'), ('3k', '3th kyu'), ('2k', '2th kyu'), ('1k', '1th kyu'), ('1d', '1th Dan'), ('2d', '2th Dan'), ('3d', '3th Dan'), ('4d', '4th Dan'), ('5d', '5th Dan'), ('6d', '6th Dan'), ('7d', '7th Dan'), ('8d', '8th Dan'), ('9d', '9th Dan'), ('10d', '10th Dan')], default='10k'),
        ),
    ]
