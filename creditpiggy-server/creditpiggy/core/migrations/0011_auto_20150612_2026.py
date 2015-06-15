# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0010_piggyuser_timezone'),
    ]

    operations = [
        migrations.AlterField(
            model_name='campaign',
            name='end_time',
            field=models.DateTimeField(default=datetime.datetime.now),
        ),
        migrations.AlterField(
            model_name='campaign',
            name='start_time',
            field=models.DateTimeField(default=datetime.datetime.now),
        ),
    ]
