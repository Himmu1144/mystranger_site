# Generated by Django 4.1.5 on 2023-06-23 21:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mystranger_app', '0006_universityprofile'),
    ]

    operations = [
        migrations.AlterField(
            model_name='universityprofile',
            name='name',
            field=models.CharField(max_length=100),
        ),
    ]