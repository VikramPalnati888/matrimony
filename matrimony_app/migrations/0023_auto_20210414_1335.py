# Generated by Django 2.2.5 on 2021-04-14 08:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('matrimony_app', '0022_remove_nulldatarequest_created_at'),
    ]

    operations = [
        migrations.CreateModel(
            name='College',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('college', models.CharField(max_length=100)),
            ],
            options={
                'unique_together': {('college',)},
            },
        ),
        migrations.CreateModel(
            name='VisibleDataRequest',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('main_user_id', models.CharField(max_length=100, null=True)),
                ('vidsible_user_id', models.CharField(max_length=100, null=True)),
                ('key_name', models.CharField(max_length=100, null=True)),
                ('visible_status', models.CharField(choices=[('Pending', 'Pending'), ('Visible', 'Visible'), ('Unvisible', 'Unvisible')], default='Pending', max_length=25)),
                ('key_data', models.CharField(max_length=100, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Weight',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('weight', models.CharField(max_length=100)),
            ],
            options={
                'unique_together': {('weight',)},
            },
        ),
        migrations.DeleteModel(
            name='NullDataRequest',
        ),
    ]