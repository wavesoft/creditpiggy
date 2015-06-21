# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import creditpiggy.core.models
import creditpiggy.core.metrics


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0012_auto_20150615_0048'),
    ]

    operations = [
        migrations.CreateModel(
            name='PiggyProjectGroup',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('uuid', models.CharField(default=creditpiggy.core.models.new_uuid, help_text=b'A unique ID identifying the specified group', unique=True, max_length=32, db_index=True)),
                ('display_name', models.CharField(help_text=b"Group's full name", max_length=1024)),
                ('projects', models.ManyToManyField(to='core.PiggyProject')),
            ],
            bases=(creditpiggy.core.metrics.MetricsModelMixin, models.Model),
        ),
    ]
