# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2017-06-09 05:58
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0008_alter_user_username_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='News',
            fields=[
                ('title', models.CharField(max_length=80)),
                ('category', models.CharField(max_length=20)),
                ('src', models.CharField(max_length=20)),
                ('pic', models.URLField()),
                ('weburl', models.URLField(primary_key=True, serialize=False)),
                ('time', models.DateTimeField(default=django.utils.timezone.now)),
                ('tags', models.CharField(default='', max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, serialize=False, to=settings.AUTH_USER_MODEL)),
                ('click_history', models.TextField(default='')),
                ('label', models.TextField(default='')),
            ],
        ),
    ]
