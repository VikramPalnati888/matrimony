# Generated by Django 2.2.5 on 2021-04-14 11:01

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('matrimony_app', '0023_auto_20210414_1335'),
    ]

    operations = [
        migrations.RenameField(
            model_name='visibledatarequest',
            old_name='key_data',
            new_name='visible_user_id',
        ),
        migrations.RemoveField(
            model_name='visibledatarequest',
            name='vidsible_user_id',
        ),
    ]
