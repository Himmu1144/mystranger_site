# Generated by Django 4.1.5 on 2023-05-17 20:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0002_alter_account_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='account',
            name='university_name',
            field=models.CharField(default='Unknown', max_length=100),
        ),
    ]
