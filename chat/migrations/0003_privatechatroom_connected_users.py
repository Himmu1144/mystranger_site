# Generated by Django 4.1.5 on 2023-09-19 23:12

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('chat', '0002_roomchatmessage_read'),
    ]

    operations = [
        migrations.AddField(
            model_name='privatechatroom',
            name='connected_users',
            field=models.ManyToManyField(blank=True, related_name='connected_users', to=settings.AUTH_USER_MODEL),
        ),
    ]
