# Generated by Django 2.2.5 on 2021-04-08 13:02

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('matrimony_app', '0017_friendrequests_status'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserMultiFile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('files', models.FileField(null=True, upload_to='profile_pic/')),
                ('basic_details', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='matrimony_app.UserBasicDetails')),
            ],
        ),
    ]