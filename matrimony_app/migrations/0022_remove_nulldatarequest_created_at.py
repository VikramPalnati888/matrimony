# Generated by Django 2.2.5 on 2021-04-12 06:22

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('matrimony_app', '0021_nulldatarequest'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='nulldatarequest',
            name='created_at',
        ),
    ]
