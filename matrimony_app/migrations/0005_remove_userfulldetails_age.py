# Generated by Django 2.2.5 on 2021-03-01 15:44

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('matrimony_app', '0004_auto_20210301_1939'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='userfulldetails',
            name='age',
        ),
    ]
