# Generated by Django 4.1.5 on 2024-01-07 15:53

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import mptt.fields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='CPublicChatRoom',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255)),
                ('question', models.CharField(max_length=2005)),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('confesserid', models.CharField(max_length=105)),
                ('taggie_token', models.CharField(blank=True, max_length=2005, null=True)),
                ('owner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='CPublicChatRoom', to=settings.AUTH_USER_MODEL)),
                ('taggie', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='CPublicChatRoomTaggie', to=settings.AUTH_USER_MODEL)),
                ('users', models.ManyToManyField(help_text='users who are connected to chat room.', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='CPublicRoomChatMessage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('content', models.TextField()),
                ('emoji', models.CharField(max_length=2)),
                ('reply_to', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='confessions.cpublicroomchatmessage')),
                ('room', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='confessions.cpublicchatroom')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='CAnswer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('content', models.TextField()),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('is_like_action', models.BooleanField(default=False, editable=False)),
                ('is_report_action', models.BooleanField(default=False, editable=False)),
                ('lft', models.PositiveIntegerField(editable=False)),
                ('rght', models.PositiveIntegerField(editable=False)),
                ('tree_id', models.PositiveIntegerField(db_index=True, editable=False)),
                ('level', models.PositiveIntegerField(editable=False)),
                ('ans_reports', models.ManyToManyField(blank=True, help_text='Reports', related_name='Cans_reports', to=settings.AUTH_USER_MODEL)),
                ('likes', models.ManyToManyField(blank=True, help_text='Likes', related_name='Clikes', to=settings.AUTH_USER_MODEL)),
                ('parent', mptt.fields.TreeForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='Cchildren', to='confessions.canswer')),
                ('question', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='Canswers', to='confessions.cpublicchatroom')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
    ]