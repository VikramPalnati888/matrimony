# Generated by Django 2.2.5 on 2021-03-02 11:26

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('matrimony_app', '0005_remove_userfulldetails_age'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='city',
            unique_together={('city',)},
        ),
        migrations.AlterUniqueTogether(
            name='country',
            unique_together={('country',)},
        ),
        migrations.AlterUniqueTogether(
            name='state',
            unique_together={('state',)},
        ),
    ]
