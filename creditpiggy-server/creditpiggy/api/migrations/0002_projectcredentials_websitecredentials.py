# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import creditpiggy.core.models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0014_auto_20150616_1247'),
        ('api', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='ProjectCredentials',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('token', models.CharField(default=creditpiggy.core.models.new_uuid, help_text=b'Anonymous authentication token for the credentials', unique=True, max_length=32, db_index=True)),
                ('secret', models.CharField(default=creditpiggy.core.models.gen_token_key, help_text=b'Shared secret between project and administrator', max_length=48)),
                ('project', models.ForeignKey(to='core.PiggyProject')),
            ],
        ),
        migrations.CreateModel(
            name='WebsiteCredentials',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('token', models.CharField(default=creditpiggy.core.models.new_uuid, help_text=b'Anonymous authentication token for the website', unique=True, max_length=32, db_index=True)),
                ('domains', models.TextField(default=b'[]')),
            ],
        ),
    ]
