# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import creditpiggy.core.models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_creditslot_piggyproject_projectuserrole'),
    ]

    operations = [
        migrations.CreateModel(
            name='ProjectCredentials',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('token', models.CharField(default=creditpiggy.core.models.new_uuid, help_text=b'Anonymous authentication token for the credentials', unique=True, max_length=32, db_index=True)),
                ('secret', models.CharField(default=creditpiggy.core.models.gen_token_key, help_text=b'Shared secret between project and administrator', unique=True, max_length=48, db_index=True)),
                ('project', models.ForeignKey(to='core.PiggyProject')),
            ],
        ),
    ]
