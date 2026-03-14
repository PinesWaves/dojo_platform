from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user_management', '0005_alter_user_medical_cond'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='accept_priv_pol',
            field=models.BooleanField(default=False),
        ),
    ]
