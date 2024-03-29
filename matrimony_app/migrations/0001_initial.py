# Generated by Django 2.1.5 on 2021-02-21 15:17

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Partner_Preferences',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('age', models.CharField(max_length=100, null=True)),
                ('height', models.CharField(max_length=100, null=True)),
                ('physical_status', models.CharField(max_length=100, null=True)),
                ('mother_tongue', models.CharField(max_length=100, null=True)),
                ('marital_status', models.CharField(max_length=100, null=True)),
                ('diet_preference', models.CharField(max_length=100, null=True)),
                ('drinking_habbit', models.CharField(max_length=100, null=True)),
                ('smoking_habbit', models.CharField(max_length=100, null=True)),
                ('caste', models.CharField(max_length=100, null=True)),
                ('religion', models.CharField(max_length=100, null=True)),
                ('star', models.CharField(max_length=100, null=True)),
                ('occupation', models.CharField(max_length=100, null=True)),
                ('under_graduation', models.CharField(max_length=100, null=True)),
                ('post_graduation', models.CharField(max_length=100, null=True)),
                ('super_speciality', models.CharField(max_length=100, null=True)),
                ('annual_income', models.CharField(max_length=100, null=True)),
                ('job_sector', models.CharField(max_length=100, null=True)),
                ('city', models.CharField(max_length=100, null=True)),
                ('state', models.CharField(max_length=100, null=True)),
                ('country', models.CharField(max_length=100, null=True)),
                ('citizenship', models.CharField(max_length=100, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='SaveOTP',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('otp', models.IntegerField(null=True)),
            ],
        ),
        migrations.CreateModel(
            name='UserBasicDetails',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('matrimony_id', models.CharField(max_length=20, null=True)),
                ('phone_number', models.CharField(max_length=20, null=True)),
                ('user', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='UserFullDetails',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=20, null=True)),
                ('gender', models.CharField(max_length=20, null=True)),
                ('dateofbirth', models.CharField(max_length=20, null=True)),
                ('image', models.ImageField(upload_to='profile_pic/')),
                ('age', models.CharField(max_length=100, null=True)),
                ('height', models.CharField(max_length=100, null=True)),
                ('physical_status', models.CharField(max_length=100, null=True)),
                ('weight', models.CharField(max_length=100, null=True)),
                ('body_type', models.CharField(max_length=100, null=True)),
                ('marital_status', models.CharField(max_length=100, null=True)),
                ('mother_tongue', models.CharField(max_length=100, null=True)),
                ('food_type', models.CharField(max_length=100, null=True)),
                ('drink_habbit', models.CharField(max_length=100, null=True)),
                ('smoke_habbit', models.CharField(max_length=100, null=True)),
                ('birth_time', models.CharField(max_length=100, null=True)),
                ('birth_place', models.CharField(max_length=100, null=True)),
                ('gotram', models.CharField(max_length=100, null=True)),
                ('star', models.CharField(max_length=100, null=True)),
                ('rashi', models.CharField(max_length=100, null=True)),
                ('caste', models.CharField(max_length=100, null=True)),
                ('sub_caste', models.CharField(max_length=100, null=True)),
                ('religion', models.CharField(max_length=100, null=True)),
                ('city', models.CharField(max_length=100, null=True)),
                ('state', models.CharField(max_length=100, null=True)),
                ('country', models.CharField(max_length=100, null=True)),
                ('citizenship', models.CharField(max_length=100, null=True)),
                ('occupation', models.CharField(max_length=100, null=True)),
                ('graduation', models.CharField(max_length=100, null=True)),
                ('graduation_status', models.CharField(max_length=100, null=True)),
                ('annual_income', models.CharField(max_length=100, null=True)),
                ('job_sector', models.CharField(max_length=100, null=True)),
                ('college', models.CharField(max_length=100, null=True)),
                ('total_family_members', models.CharField(max_length=100, null=True)),
                ('father_details', models.CharField(max_length=100, null=True)),
                ('mother_details', models.CharField(max_length=100, null=True)),
                ('brother_details', models.CharField(max_length=100, null=True)),
                ('sister_details', models.CharField(max_length=100, null=True)),
                ('basic_details', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='matrimony_app.UserBasicDetails')),
            ],
        ),
        migrations.CreateModel(
            name='Viewed_matches',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('viewed_user_id', models.CharField(max_length=100, null=True)),
                ('viewd_status', models.BooleanField(default=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='saveotp',
            name='phone_number',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='matrimony_app.UserBasicDetails'),
        ),
        migrations.AddField(
            model_name='partner_preferences',
            name='basic_details',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='matrimony_app.UserBasicDetails'),
        ),
        migrations.AlterUniqueTogether(
            name='userbasicdetails',
            unique_together={('phone_number', 'matrimony_id')},
        ),
        migrations.AlterUniqueTogether(
            name='saveotp',
            unique_together={('phone_number',)},
        ),
    ]
