# Generated by Django 2.2.5 on 2021-03-18 16:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('matrimony_app', '0007_imagetest'),
    ]

    operations = [
        migrations.DeleteModel(
            name='imagetest',
        ),
        migrations.RenameField(
            model_name='partner_preferences',
            old_name='age',
            new_name='max_age',
        ),
        migrations.AddField(
            model_name='partner_preferences',
            name='min_age',
            field=models.CharField(max_length=100, null=True),
        ),
    ]
