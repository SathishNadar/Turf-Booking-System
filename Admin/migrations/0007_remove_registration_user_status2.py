# Generated by Django 4.2.20 on 2025-04-06 13:12

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Admin', '0006_registration_user_status2'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='registration',
            name='user_status2',
        ),
    ]
