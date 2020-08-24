# Generated by Django 3.1 on 2020-08-24 13:23

import datetime
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Company',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=128)),
                ('email', models.CharField(max_length=128)),
                ('communication_configuration', models.JSONField(blank=True, help_text='        {\n            "matrix_domain": "https://matrix.example.com/",\n            "matrix_user_facing_domain": "https://example.com/",\n            "matrix_user": "ctt",\n            "matrix_password": "password_here",\n            "matrix_room_id": "!DnlKuYFaiXXweICFTd:example.com"\n        }\n        ', null=True)),
            ],
        ),
        migrations.CreateModel(
            name='TeamMember',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=128)),
                ('is_active', models.BooleanField(default=True)),
                ('company', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='members', to='reminder.company')),
            ],
        ),
        migrations.CreateModel(
            name='Worklog',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(default=datetime.datetime.now)),
                ('pushed', models.BooleanField(default=False)),
                ('pushed_at', models.DateTimeField(blank=True, null=True)),
                ('last_notified', models.DateTimeField(blank=True, null=True)),
                ('team_member', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='worklogs', to='reminder.teammember')),
            ],
        ),
        migrations.CreateModel(
            name='Communication',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('value', models.CharField(max_length=128)),
                ('type', models.CharField(choices=[('EMAIL', 'Email'), ('MATRIX', 'Matrix')], max_length=32)),
                ('team_member', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='communications', to='reminder.teammember')),
            ],
        ),
    ]
