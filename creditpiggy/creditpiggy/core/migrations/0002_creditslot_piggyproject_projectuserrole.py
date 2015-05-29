# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import creditpiggy.core.models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='CreditSlot',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
            ],
        ),
        migrations.CreateModel(
            name='PiggyProject',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('uuid', models.CharField(default=creditpiggy.core.models.new_uuid, help_text=b'A unique ID identifying the specified project', unique=True, max_length=32, db_index=True)),
                ('display_name', models.CharField(help_text=b"Project's full name", max_length=1024)),
                ('desc', models.TextField(help_text=b'Project description')),
                ('profileImage', models.CharField(help_text=b"Project's profile image", max_length=1024)),
            ],
        ),
        migrations.CreateModel(
            name='ProjectUserRole',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('role', models.IntegerField(default=3, choices=[(0, b'Owner'), (1, b'Administrator'), (2, b'Moderator'), (3, b'Member')])),
                ('project', models.ForeignKey(to='core.PiggyProject')),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
