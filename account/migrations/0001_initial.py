# Generated by Django 4.1.5 on 2023-11-30 10:54

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Account',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('email', models.EmailField(max_length=100, unique=True, verbose_name='email')),
                ('name', models.CharField(default='Stranger', max_length=100)),
                ('university_name', models.CharField(default='Unknown', max_length=100)),
                ('origin', models.BooleanField(default=False)),
                ('flags', models.IntegerField(blank=True, default=0)),
                ('date_joined', models.DateTimeField(auto_now_add=True, verbose_name='date joined')),
                ('last_login', models.DateTimeField(auto_now=True, verbose_name='last login')),
                ('is_admin', models.BooleanField(default=False)),
                ('is_active', models.BooleanField(default=True)),
                ('is_staff', models.BooleanField(default=False)),
                ('is_superuser', models.BooleanField(default=False)),
                ('terms', models.BooleanField(default=True)),
                ('is_verified', models.BooleanField(default=False)),
                ('gender', models.CharField(choices=[('M', 'Male'), ('F', 'Female')], default='M', max_length=1, verbose_name='Gender')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='deleted_account',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('email', models.CharField(max_length=150)),
                ('name', models.CharField(max_length=100)),
                ('reason', models.CharField(max_length=10000)),
                ('is_resolved', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='RegistrationError',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('email', models.CharField(max_length=100)),
                ('uni_name', models.CharField(max_length=100)),
                ('uni_address', models.CharField(max_length=400)),
                ('issue_faced', models.CharField(max_length=10000)),
                ('is_resolved', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='AccountToken',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('auth_token', models.CharField(max_length=100)),
                ('is_verified', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
