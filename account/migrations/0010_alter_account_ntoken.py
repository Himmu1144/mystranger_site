# Generated by Django 4.1.5 on 2024-01-27 01:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0009_account_ntoken'),
    ]

    operations = [
        migrations.AlterField(
            model_name='account',
            name='ntoken',
            field=models.CharField(blank=True, default='None', max_length=1000, null=True),
        ),
    ]
